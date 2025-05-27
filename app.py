from flask import Flask, request, jsonify, render_template
from rdflib import Graph
import requests  # necesario para redirigir la consulta a DBpedia

app = Flask(__name__)

#ontología local
g = Graph()

try:
    g.parse("ontologia/oficial.rdf", format="xml")
    print("Ontología cargada correctamente.")
except Exception as e:
    print(f"Error al cargar la ontología RDF: {e}")
    g = None

#página principal que carga el HTML
@app.route("/")
def home():
    return render_template("index.html")

# Ruta para ejecutar consultas SPARQL
@app.route("/sparql", methods=["POST"])
def ejecutar_sparql():
    data = request.get_json()
    query = data.get('query')

    if not query:
        return jsonify({"error": "Falta el campo 'query'"}), 400

    try:
        if "dbr:" in query or "dbo:" in query:
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

        if g is None:
            return jsonify({"error": "La ontología no está cargada"}), 500

        resultados = g.query(query)
        respuesta = [
            {str(var): str(fila[var]) for var in fila.labels}
            for fila in resultados
        ]
        return jsonify({"resultados": respuesta, "total": len(respuesta)})

    except Exception as e:
        return jsonify({"error": "Error al ejecutar la consulta", "detalle": str(e)}), 500

#manejador de errores
@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", mensaje="Error interno del servidor."), 500

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", mensaje="Página no encontrada."), 404

if __name__ == "__main__":
    app.run(debug=True)