import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

load_dotenv()

class Neo4jClient:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USERNAME")
        self.password = os.getenv("NEO4J_PASSWORD")
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))

    def close(self):
        self.driver.close()

    def add_ship(self, ship_id, name, lat, lng):
        """Creates a new ship node."""
        query = "CREATE (s:Ship {id: $id, name: $name, lat: $lat, lng: $lng, status: 'Moving'})"
        with self.driver.session() as session:
            session.run(query, id=ship_id, name=name, lat=float(lat), lng=float(lng))

    def get_all_ships(self):
        """Fetches all ships for the dashboard."""
        query = "MATCH (s:Ship) RETURN s.id as id, s.name as name, s.lat as lat, s.lng as lng, s.status as status"
        with self.driver.session() as session:
            result = session.run(query)
            return [record.data() for record in result]

    def get_impacted_customers(self, ship_id):
        """Finds the actual customers linked to a specific ship via the supply chain path."""
        query = """
        MATCH (s:Ship {id: $ship_id})-[:CARRIES]->(p:Product)-[:DESTINED_FOR]->(w:Warehouse)-[:SUPPLIES]->(c:Customer)
        RETURN c.name as customer, p.name as product, p.price as value
        """
        with self.driver.session() as session:
            result = session.run(query, ship_id=ship_id)
            # This returns a list of dictionaries like [{'customer': 'Parishram', ...}]
            return [record.data() for record in result]