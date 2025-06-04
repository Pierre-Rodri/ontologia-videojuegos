import os
from dotenv import load_dotenv
from rdflib import Graph

load_dotenv()

OPENAI_API_KEY = os.getenv("API_key")

def cargar_ontologia():
    g = Graph()
    try:
        g.parse("ontologia/oficial.rdf", format="xml")
        print("Ontología cargada correctamente.")
        return g
    except Exception as e:
        print(f"Error al cargar la ontología RDF: {e}")
        return None
