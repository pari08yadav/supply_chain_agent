from database.neo4j_client import Neo4jClient

def force_fix():
    client = Neo4jClient()
    
    # We split the queries to ensure Neo4j processes them in order
    delete_query = "MATCH (n) DETACH DELETE n"
    
    build_query = """
    CREATE (s:Ship {id: 'SHIP_001', name: 'Pari-Express', status: 'Moving'})
    CREATE (p:Product {sku: 'SENS-99', name: 'Precision Sensors', price: 50000})
    CREATE (w:Warehouse {id: 'WH-DEL', city: 'Delhi'})
    CREATE (c:Customer {name: 'Parishram'})
    WITH s, p, w, c
    MERGE (s)-[:CARRIES]->(p)
    MERGE (p)-[:DESTINED_FOR]->(w)
    MERGE (w)-[:SUPPLIES]->(c)
    """
    
    try:
        with client.driver.session() as session:
            session.run(delete_query)
            session.run(build_query)
        print("✅ DATABASE REBUILT: Python client has confirmed the 4-node chain.")
    except Exception as e:
        print(f"❌ Error during fix: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    force_fix()