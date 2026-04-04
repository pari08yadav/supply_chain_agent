# from database.neo4j_client import Neo4jClient

# def build_the_bridge():
#     client = Neo4jClient()
    
#     # This Cypher query connects the existing Ships to new Products and Warehouses
#     bridge_query = """
#     // 1. Create Products
#     MERGE (p1:Product {sku: 'SENS-99', name: 'Precision Sensors', price: 50000})
#     MERGE (p2:Product {sku: 'MTR-01', name: 'Industrial Motors', price: 20000})

#     // 2. Create Warehouses
#     MERGE (w1:Warehouse {id: 'WH-DEL', city: 'Delhi', capacity: 10000})
#     MERGE (w2:Warehouse {id: 'WH-MUM', city: 'Mumbai', capacity: 8000})

#     // --- The Bridge ---
#     WITH p1, w1

#     // 3. Connect Ships to Products (Assumes SHIP_001 exists from your UI)
#     MATCH (s:Ship {id: 'SHIP_001'}) 
#     MERGE (s)-[:CARRIES]->(p1)

#     // 4. Connect Products to Warehouses
#     MERGE (p1)-[:DESTINED_FOR]->(w1)

#     // 5. Connect Warehouses to Customers (Assumes Customer exists from your UI)
#     WITH w1
#     MATCH (c:Customer)
#     MERGE (w1)-[:SUPPLIES]->(c)
#     """
    
#     with client.driver.session() as session:
#         session.run(bridge_query)
    
#     print("✅ Supply Chain Bridge built! Ship -> Product -> Warehouse -> Customer is now connected.")
#     client.close()

# if __name__ == "__main__":
#     build_the_bridge()



from database.neo4j_client import Neo4jClient

def build_the_bridge():
    client = Neo4jClient()
    
    # Updated query to ensure data is passed between sections correctly
    bridge_query = """
    // 1. Create/Find Products
    MERGE (p1:Product {sku: 'SENS-99', name: 'Precision Sensors', price: 50000})
    MERGE (p2:Product {sku: 'MTR-01', name: 'Industrial Motors', price: 20000})

    // 2. Create/Find Warehouses
    MERGE (w1:Warehouse {id: 'WH-DEL', city: 'Delhi', capacity: 10000})
    MERGE (w2:Warehouse {id: 'WH-MUM', city: 'Mumbai', capacity: 8000})

    // --- PASS EVERYTHING FORWARD ---
    WITH p1, p2, w1, w2

    // 3. Connect Ships to Products
    // We use MERGE for the Ship here just in case you haven't added it in UI yet
    MERGE (s:Ship {id: 'SHIP_001'})
    ON CREATE SET s.name = 'Pari-Express', s.status = 'Moving'
    MERGE (s)-[:CARRIES]->(p1)

    // 4. Connect Products to Warehouses
    MERGE (p1)-[:DESTINED_FOR]->(w1)
    MERGE (p2)-[:DESTINED_FOR]->(w2)

    // 5. Connect Warehouses to Customers
    WITH w1, w2
    MATCH (c:Customer) // Finds every customer you added via UI
    MERGE (w1)-[:SUPPLIES]->(c)
    """
    
    try:
        with client.driver.session() as session:
            session.run(bridge_query)
        print("✅ Supply Chain Bridge built! Ship -> Product -> Warehouse -> Customer is now connected.")
    except Exception as e:
        print(f"❌ Cypher Error: {e}")
    finally:
        client.close()

if __name__ == "__main__":
    build_the_bridge()