import re
import os
from langgraph.graph import StateGraph, END
from core.state import AgentState
from database.neo4j_client import Neo4jClient
from database.qdrant import QdrantManager 
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langgraph.checkpoint.memory import MemorySaver

# Initialize Phase 1 Tools
n_db = Neo4jClient()
q_db = QdrantManager()
memory = MemorySaver()

# Initialize Gemini
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0.1 # Lower temperature for more accurate math/logic
)

# --- NODE 1: The Extractor ---
def extract_incident_details(state: AgentState):
    report = state["incident_report"]
    ship_match = re.search(r"SHIP_\d+", report)
    ship_id = ship_match.group(0) if ship_match else "UNKNOWN"
    return {
        "ship_id": ship_id, 
        "steps_taken": [f"🔍 Analyzed report. Identified Ship ID: {ship_id}"]
    }

# --- NODE 2: Graph Searcher (Fixed for your new Neo4j logic) ---
def lookup_impacted_customers(state: AgentState):
    ship_id = state["ship_id"]
    
    if ship_id == "UNKNOWN":
        return {
            "impacted_customers": [],
            "steps_taken": ["⚠️ Neo4j: Ship ID unknown. Skipping graph lookup."]
        }
        
    results = n_db.get_impacted_customers(ship_id)
    
    # We now store the FULL dictionary [{'customer': 'Name', 'product': 'Item'}]
    # This allows the next node to use the name for filtering
    return {
        "impacted_customers": results, 
        "steps_taken": [f"🕸️ Neo4j: Found {len(results)} customers linked to {ship_id}."]
    }

# --- NODE 3: Legal Researcher (UPDATED WITH FILTERING) ---
def lookup_legal_penalties(state: AgentState):
    customers_data = state["impacted_customers"]
    all_clauses = []
    
    for entry in customers_data:
        customer_name = entry.get('customer')
        if customer_name:
            # We now pass the customer_name to use the Metadata Filter
            query = f"What are the delay penalty clauses for {customer_name}?"
            clauses = q_db.search_contract_logic(query, customer_name=customer_name)
            all_clauses.extend(clauses)
            
    return {
        "relevant_clauses": list(set(all_clauses)), # Remove duplicates
        "steps_taken": [f"📜 Qdrant: Retrieved {len(all_clauses)} specific penalty clauses."]
    }

# --- NODE 4: Logic/Calculator ---
def calculate_risk(state: AgentState):
    clauses_text = "\n".join(state["relevant_clauses"])
    incident = state["incident_report"]
   
    if not clauses_text:
        return {
            "total_penalty_amount": 0.0, 
            "steps_taken": ["⚖️ Logic: No specific clauses found to calculate."]
        }

    prompt = f"""
    Incident Report: {incident}
    Legal Clauses: {clauses_text}
    
    Based on the delay mentioned in the incident and the penalty terms in the clauses, 
    calculate the total financial risk.
    
    Return ONLY the numerical value (e.g., 500.0). Do not include currency symbols or text.
    If no penalty applies, return 0.0.
    """
    
    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        # Clean the AI response to get just the number
        clean_val = re.sub(r'[^\d.]', '', response.content.strip())
        total = float(clean_val)
    except:
        total = 0.0
        
    return {
        "total_penalty_amount": total,
        "steps_taken": [f"⚖️ AI Reasoning: Interpreted contracts and calculated ${total} risk."]
    }



def chat_with_investigator(state: AgentState):
    """Allows the user to ask follow-up questions about the incident."""
    # Safety check for messages
    if not state.get("messages"):
        return {"messages": [AIMessage(content="How can I help you today?")]}
        
    last_message = state["messages"][-1].content
    
    context = f"""
    You are the Supply Chain AI Assistant. 
    Investigation Context: {state.get('incident_report', 'None')}
    Ship: {state.get('ship_id', 'Unknown')}
    Calculated Risk: ${state.get('total_penalty_amount', 0.0)}
    Found Clauses: {state.get('relevant_clauses', [])}
    """
    
    # Use SystemMessage for the context
    prompt = [
        SystemMessage(content=context),
        HumanMessage(content=last_message)
    ]
    
    response = llm.invoke(prompt)
    return {"messages": [response]}



def route_request(state: AgentState):
    """
    Decides where to enter the graph.
    If 'incident_report' is present, we are starting a new investigation.
    If only 'messages' are present, the user is chatting.
    """
    # If the user just typed an incident, go to the extractor
    if state.get("incident_report") and not state.get("ship_id"):
        return "extractor"
    
    # Otherwise, it's a follow-up chat
    return "chat"


# --- CONSTRUCT THE GRAPH ---
workflow = StateGraph(AgentState)
workflow.add_node("extractor", extract_incident_details)
workflow.add_node("graph_lookup", lookup_impacted_customers)
workflow.add_node("legal_lookup", lookup_legal_penalties)
workflow.add_node("calculator", calculate_risk)
workflow.add_node("chat", chat_with_investigator)

workflow.set_entry_point("extractor")
workflow.add_edge("extractor", "graph_lookup")
workflow.add_edge("graph_lookup", "legal_lookup")
workflow.add_edge("legal_lookup", "calculator")
workflow.add_edge("calculator", END)

workflow.add_edge("chat", END)

# THE KEY: Use a conditional entry point
workflow.set_conditional_entry_point(
    route_request,
    {
        "extractor": "extractor",
        "chat": "chat"
    }
)


agent_app = workflow.compile(checkpointer=memory)