from flask import Flask, request, jsonify, render_template
from rdflib import Graph
import requests
import re

app = Flask(__name__)
g = Graph()

try:
    g.parse("ontologia/oficial.rdf", format="xml")
    print("Ontología cargada correctamente.")
except Exception as e:
    print(f"Error al cargar la ontología RDF: {e}")
    g = None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/sparql", methods=["POST"])
def ejecutar_sparql():
    data = request.get_json()
    query = data.get('query')
    endpoint = data.get('endpoint', 'local')
    lang = data.get('lang', 'en') 

    if not query:
        return jsonify({"error": "Falta el campo 'query'"}), 400
    
    try:
        if endpoint == "dbpedia":
            propiedades_idioma = [
                "rdfs:label", "rdfs:comment", "dbo:abstract", "foaf:name", "skos:prefLabel"
            ]

            #filtro inteligente a la consulta    
            query = inyectar_filtros_idioma(query, lang, propiedades_idioma)

            #Para verificar la integridad de la consulta generada
            print("Datos recibidos del frontend:", data)
            print("Endpoint:", endpoint)
            print("Idioma:", lang)
            print("\n--- Consulta SPARQL enviada a DBpedia ---")
            print(f"Idioma solicitado: {lang}")
            print(query)
            print("------------------------------------------\n")

            response = requests.get(
                "http://dbpedia.org/sparql",
                params={"query": query, "format": "application/sparql-results+json"}
            )
            
            if response.status_code != 200:
                return jsonify({
                    "error": f"DBpedia respondió con un error {response.status_code}",
                    "detalle": response.text
                }), 500

            return jsonify(response.json())

        elif endpoint == "local":
            resultados = g.query(query)
            respuesta = [
                {str(var): str(fila[var]) for var in fila.labels}
                for fila in resultados
            ]
            return jsonify({"resultados": respuesta, "total": len(respuesta)})

        else:
            return jsonify({"error": f"Fuente desconocida: {endpoint}"}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#buscamos si la consulta contiene esas propiedades.
def extraer_vars_lingüisticas(consulta, propiedades):
    vars_detectadas = set()
    for prop in propiedades:
        # busca patrones como: <algo> prop ?var .
        patron = rf"{re.escape(prop)}\s+\?(\w+)"
        matches = re.findall(patron, consulta)
        vars_detectadas.update(matches)
    return vars_detectadas

#Insertar los filtros FILTER(langMatches(...)) para cada variable detectada
def inyectar_filtros_idioma(consulta, lang, propiedades):
    # No insertar si ya hay filtros de idioma
    if "lang(" in consulta:
        return consulta

    vars_linguisticas = extraer_vars_lingüisticas(consulta, propiedades)
    if not vars_linguisticas:
        return consulta  # No hay variables a filtrar

    # Construimos bloque de filtros
    filtros = "".join(
        f"  FILTER(langMatches(lang(?{var}), \"{lang}\")) .\n" for var in vars_linguisticas
    )

    return consulta.replace("WHERE {", f"WHERE {{\n{filtros}")


@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", mensaje="Error interno del servidor."), 500

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", mensaje="Página no encontrada."), 404

if __name__ == "__main__":
    app.run(debug=True)