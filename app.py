from flask import Flask, request, jsonify, render_template
from rdflib import Graph
import requests

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
            #variable de idiomas
            vars_con_idioma = ["label", "comment", "title", "description", "name", "abstract"]

            #add filtros de idioma automáticamente si no hay filtros existentes
            if "WHERE {" in query and "lang(" not in query:
                filtros = ""
                for var in vars_con_idioma:
                    if f"?{var}" in query:
                        filtros += f'  FILTER(langMatches(lang(?{var}), "{lang}")) .\n'
                if filtros:
                    query = query.replace("WHERE {", f"WHERE {{\n{filtros}")

            #Para verificar la integridad de la consulta generada
            print("\n--- Consulta SPARQL enviada a DBpedia ---")
            print(f"Idioma solicitado: {lang}")
            print(query)
            print("------------------------------------------\n")

            #enviamos la consulta a DBpedia
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



@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", mensaje="Error interno del servidor."), 500

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", mensaje="Página no encontrada."), 404

if __name__ == "__main__":
    app.run(debug=True)