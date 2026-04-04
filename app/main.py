import streamlit as st
import pandas as pd
from database.neo4j_client import Neo4jClient
from database.qdrant import QdrantManager 
from core.graph import agent_app 
from langchain_core.messages import HumanMessage, AIMessage

st.set_page_config(page_title="Supply Chain Tower", layout="wide", page_icon="🚢")

# Initialize Clients
n_db = Neo4jClient()
q_db = QdrantManager()

# --- SESSION STATE FOR CHAT ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.title("🚢 Supply Chain AI Command Center")

# --- SIDEBAR: Admin Controls ---
with st.sidebar:
    st.header("🛠️ Admin Controls")
    if st.button("Add SHIP_001 (Test Data)"):
        n_db.add_ship("SHIP_001", "Pari-Express", 28.6, 77.2)
        st.success("Test Ship added to Neo4j!")
    
    st.divider()
    st.subheader("📝 Index New Contract")
    cust = st.text_input("Customer Name")
    terms = st.text_area("Contract Terms (e.g. Penalty is $500 for 48h)")
    if st.button("Index Contract"):
        if cust and terms:
            q_db.add_contract(cust, terms)
            st.success(f"Contract for {cust} Indexed!")
        else:
            st.error("Please provide both name and terms.")

# --- MAIN LAYOUT ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🌐 Real-time Fleet Map")
    ships = n_db.get_all_ships()
    if ships:
        df = pd.DataFrame(ships)
        if 'lat' in df.columns and 'lng' in df.columns:
            map_df = df.rename(columns={'lng': 'lon'}).dropna(subset=['lat', 'lon'])
            if not map_df.empty:
                st.map(map_df)
        st.dataframe(df, use_container_width=True)

with col2:
    st.subheader("🔍 Contract Search")
    query = st.text_input("Search legal database manually...")
    if query:
        results = q_db.search_contract_logic(query)
        for i, res in enumerate(results):
            st.info(f"Match {i+1}: {res}")

# --- PHASE 3: THE AGENTIC INVESTIGATOR ---
st.divider()
st.header("🧠 AI Incident Investigator")

incident_note = st.text_area(
    "Incident Description", 
    placeholder="Example: SHIP_001 is facing a 48-hour delay."
)

if st.button("🚀 Run AI Investigation"):
    if incident_note:
        with st.spinner("Analyzing incident..."):
            config = {"configurable": {"thread_id": "pari_investigation_001"}}
            # We pass steps_taken: [] to keep the UI clean each run
            inputs = {"incident_report": incident_note, "steps_taken": []}
            
            result = agent_app.invoke(inputs, config=config)
            
            st.success("Investigation Complete!")
            
            res_col1, res_col2, res_col3 = st.columns(3)
            with res_col1:
                st.metric("Detected Ship", result['ship_id'])
            with res_col2:
                st.metric("Impacted Customers", len(result['impacted_customers']))
            with res_col3:
                st.metric("Financial Risk", f"${result['total_penalty_amount']}")

            with st.expander("🤖 View Agent Thought Process"):
                for step in result['steps_taken']:
                    st.markdown(f"- {step}")


# --- PHASE 4: CONVERSATIONAL CHAT (STABLE VERSION) ---
st.divider()
st.header("💬 Talk to the Investigator")

# 1. ALWAYS display the history from the state first
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 2. Use the chat input
if chat_input := st.chat_input("Ask a follow-up question..."):
    
    # 3. IMMEDIATELY add to session state and show it
    st.session_state.chat_history.append({"role": "user", "content": chat_input})
    
    # 4. Generate AI Response
    with st.spinner("Analyzing context..."):
        config = {"configurable": {"thread_id": "pari_investigation_001"}}
        
        # --- THE FIX IS HERE ---
        # We need to pass the conversation as a HumanMessage AND 
        # keep the thread_id consistent so it remembers Phase 3.
        chat_result = agent_app.invoke(
            {
                "messages": [HumanMessage(content=chat_input)],
                # We don't need to re-pass ship_id/clauses if the 
                # checkpointer is working, but it helps for safety!
            }, 
            config=config
        )
        
        if "messages" in chat_result and chat_result["messages"]:
            # LangGraph stores history in 'messages'. We want the LAST one (the AI response)
            ai_response = chat_result["messages"][-1].content
            
            # 5. Add AI response to state
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            
            # 6. Rerun to show the new message and clear the input box
            st.rerun()


# # --- PHASE 4: CONVERSATIONAL CHAT (STABLE VERSION) ---
# st.divider()
# st.header("💬 Talk to the Investigator")

# # 1. ALWAYS display the history from the state first
# for message in st.session_state.chat_history:
#     with st.chat_message(message["role"]):
#         st.markdown(message["content"])

# # 2. Use the chat input
# if chat_input := st.chat_input("Ask a follow-up question..."):
    
#     # 3. IMMEDIATELY add to session state and show it
#     st.session_state.chat_history.append({"role": "user", "content": chat_input})
#     with st.chat_message("user"):
#         st.markdown(chat_input)

#     # 4. Generate AI Response
#     with st.spinner("Analyzing context..."):
#         config = {"configurable": {"thread_id": "pari_investigation_001"}}
        
#         # We invoke the agent
#         chat_result = agent_app.invoke(
#             {"messages": [HumanMessage(content=chat_input)]}, 
#             config=config
#         )
        
#         if "messages" in chat_result and chat_result["messages"]:
#             ai_response = chat_result["messages"][-1].content
            
#             # 5. Add AI response to state
#             st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            
#             # 6. Crucial: Use st.rerun() here to refresh the UI and stop the repeat!
#             st.rerun()