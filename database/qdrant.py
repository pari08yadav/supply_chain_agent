
import os
import uuid
from dotenv import load_dotenv
# We alias the library to 'QC' to make it 100% distinct
from qdrant_client import QdrantClient as QC
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from qdrant_client import models # Ensure this is imported at the top


load_dotenv()

class QdrantManager: # Renamed from QdrantClient
    def __init__(self):
        qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
        # Initialize the actual library connection
        self.remote_conn = QC(url=qdrant_url) 
        
        self.collection_name = os.getenv("COLLECTION_NAME", "sla_contracts")
        
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=os.getenv("GOOGLE_API_KEY") 
        )
        
        self._ensure_collection()

    def _ensure_collection(self):
        try:
            self.remote_conn.get_collection(self.collection_name)
        except Exception:
            self.remote_conn.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=3072, distance=Distance.COSINE)
            )

    def add_contract(self, customer_name, contract_text):
        vector = self.embeddings.embed_query(f"Customer: {customer_name}. {contract_text}")
        self.remote_conn.upsert(
            collection_name=self.collection_name,
            points=[
                PointStruct(
                    id=str(uuid.uuid4()), 
                    vector=vector, 
                    payload={"customer": customer_name, "text": contract_text}
                )
            ]
        )

    def search_contract_logic(self, query_text, customer_name=None):
        """
        Searches for contract clauses, optionally filtering by a specific customer.
        """
        vector = self.embeddings.embed_query(query_text)

        # 1. Build a filter if a customer name is provided
        search_filter = None
        if customer_name:
            search_filter = models.Filter(
                must=[
                    models.FieldCondition(
                        key="customer", 
                        match=models.MatchValue(value=customer_name)
                    )
                ]
            )

        # 2. Execute the query with the filter
        search_result = self.remote_conn.query_points(
            collection_name=self.collection_name,
            query=vector,
            query_filter=search_filter, # Apply the filter here
            limit=3 # Increased limit to get more context for the LLM
        )

        # 3. Return the results
        return [
            point.payload["text"]
            for point in search_result.points
        ]