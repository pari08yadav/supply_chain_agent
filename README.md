Since you've built a sophisticated **Agentic RAG** system, your README should reflect the high-level architecture. Here is a professional, concise README file for your project.

---

# 🚢 Supply Chain AI Command Center

An **Agentic AI Investigator** that automates ship delay analysis, customer impact mapping, and legal penalty calculations using  **Graph Databases** ,  **Vector Search** , and  **Generative AI** .

## 🌟 Overview

This project solves the "Delayed Shipment" problem by connecting three distinct data silos:

1. **Fleet Logistics (Neo4j):** Tracking which ships carry which products for which customers.
2. **Legal Contracts (Qdrant):** Storing and searching unstructured PDF/Text contract clauses.
3. **Reasoning (Gemini + LangGraph):** A multi-node AI agent that "thinks" through an incident to calculate financial risk.

---

## 🛠️ Tech Stack

* **Orchestration:** [LangGraph](https://github.com/langchain-ai/langgraph) (Stateful multi-actor agent)
* **LLM:** [Google Gemini 2.5 Flash](https://ai.google.dev/)
* **Graph Database:** [Neo4j](https://neo4j.com/) (Relationship mapping)
* **Vector Database:** [Qdrant](https://qdrant.tech/) (Contract Retrieval)
* **Frontend:** [Streamlit](https://streamlit.io/) (Real-time dashboard)

---

## 🧠 Agent Architecture

The agent follows a strict 4-step logical pipeline to ensure accuracy:

1. **Extraction Node:** Uses RegEx to identify the specific `SHIP_ID` from raw incident text.
2. **Graph Lookup Node:** Queries Neo4j to find the **Customer** linked to the ship.
3. **Legal Lookup Node:** Performs a semantic vector search in Qdrant to find the **Penalty Clauses** for that specific customer.
4. **Risk Calculator Node:** Uses Gemini to compare the delay time against the contract threshold and output a final  **Dollar ($) Amount** .

---

## 🚀 Features

* **Real-time Map:** Visualize fleet coordinates using Streamlit maps.
* **Contract Indexing:** Upload and "vectorize" new customer contracts on the fly.
* **Stateful Memory:** A built-in **Chat Investigator** that remembers previous investigations so you can ask follow-up questions (e.g.,  *"Why was the penalty $1000?"* ).
* **Audit Trail:** View the "Agent Thought Process" to see exactly how the AI moved from a ship ID to a final penalty.

---

## ⚙️ Installation & Setup

1. **Clone the Repository:**
   **Bash**

   ```
   git clone https://github.com/your-username/supply-chain-ai.git
   cd supply-chain-ai
   ```
2. **Environment Variables:**
   Create a `.env` file and add your keys:
   **Code snippet**

   ```
   GOOGLE_API_KEY=your_gemini_key
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=your_password
   QDRANT_URL=http://localhost:6333
   ```
3. **Run the Application:**
   **Bash**

   ```
   streamlit run app/main.py
   ```

---

## 📈 Future Roadmap

* **Automated Email Alerts:** Notify customers automatically when a penalty is triggered.
* **Weather Integration:** Use external APIs to verify if "Act of God" clauses apply to delays.
* **Multi-Ship Impact:** Analyze incidents that block entire ports or shipping lanes.

---

**Developed with ❤️ by Parishram Yadav**
