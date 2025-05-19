from flask import Flask, request, jsonify, render_template
from rdflib import Graph

app = Flask(__name__)

g = Graph()
g.parse("ontologia/oficial.rdf", format="xml")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/sparql", methods=["POST"])
def ejecutar_sparql():
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "Falta el campo 'query'"}), 400

    try:
        resultados = g.query(query)
        respuesta = [
            {str(var): str(fila[var]) for var in fila.labels}
            for fila in resultados
        ]
        return jsonify(respuesta)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
