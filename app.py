from flask import Flask, request, jsonify, render_template
from rdflib import Graph
import requests  # necesario para redirigir la consulta a DBpedia

app = Flask(__name__)

# Cargar tu ontología local
g = Graph()
try:
    g.parse("ontologia/oficial.rdf", format="xml")
except Exception as e:
    print(f"Error al cargar la ontología RDF: {e}")
    g = None

# Página principal que carga el HTML
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

            try:
                return jsonify(response.json())
            except Exception as e:
                return jsonify({
                    "error": f"No se pudo decodificar la respuesta JSON de DBpedia",
                    "detalle": str(e),
                    "respuesta": response.text[:200]  # mostrar primeros caracteres por si es HTML
                }), 500


        # 🔍 Consulta local a tu RDF
        resultados = g.query(query)
        respuesta = [
            {str(var): str(fila[var]) for var in fila.labels}
            for fila in resultados
        ]
        return jsonify(respuesta)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

#manejador de errores
@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", mensaje="Error interno del servidor."), 500

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", mensaje="Página no encontrada."), 404

if __name__ == "__main__":
    app.run(debug=True)