from typing import Annotated, List, TypedDict, Sequence
from langchain_core.messages import BaseMessage
import operator

class AgentState(TypedDict):
    # 1. The Raw Input (e.g., "SHIP_001 is 48 hours delayed")
    incident_report: str
    
    # 2. The ID extracted from the report
    ship_id: str
    
    # 3. List of customers found in the Neo4j Graph
    impacted_customers: List[str]
    
    # 4. Specific legal clauses retrieved from Qdrant
    relevant_clauses: List[str]
    
    # 5. The final calculated penalty in USD
    total_penalty_amount: float
    
    # 6. A log of every step the agent takes (Append-only)
    steps_taken: list

    messages: Annotated[Sequence[BaseMessage], operator.add]