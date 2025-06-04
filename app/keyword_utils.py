import re
from app.sparql_utils import ejecutar_sparql

def buscar_por_keyword(keyword, endpoint, lang):
    keyword = limpiar_entrada(keyword)

    if endpoint == "dbpedia":
        query = f"""
        PREFIX dbo: <http://dbpedia.org/ontology/>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

        SELECT ?game ?title ?description
        WHERE {{
          ?game a dbo:VideoGame ;
                rdfs:label ?title ;
                rdfs:comment ?description .
          FILTER (
            CONTAINS(LCASE(?title), LCASE("{keyword}")) ||
            CONTAINS(LCASE(?description), LCASE("{keyword}"))
          )
          FILTER(lang(?title) = "{lang}")
          FILTER(lang(?description) = "{lang}")
        }}
        LIMIT 20
        """
    else:
        query = f"""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX : <http://www.semanticweb.org/juaco/ontologies/2024/0/videojuegos#>

        SELECT ?videojuego ?label
        WHERE {{
          ?videojuego a :Videojuego ;
                      rdfs:label ?label .
          FILTER (CONTAINS(LCASE(?label), LCASE("{keyword}")))
          FILTER(lang(?label) = "{lang}")
        }}
        LIMIT 20
        """

    return ejecutar_sparql(query, endpoint, lang)

def limpiar_entrada(texto):
    return re.sub(r'[^a-zA-Z0-9áéíóúÁÉÍÓÚñÑüÜ\s\-_:]', '', texto)
