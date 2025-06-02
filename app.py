from flask import Flask, request, jsonify, render_template
from rdflib import Graph
from rdflib.plugins.sparql.parser import parseQuery
from dotenv import load_dotenv
import requests
import re
import openai
import os

#inicialización
app = Flask(__name__)
g = Graph()
load_dotenv()

#configuración de API
openai.api_key = os.getenv("API_key")
client = openai.OpenAI(api_key=openai.api_key)

if not openai.api_key:
    raise ValueError("No se encontró la clave API de OpenAI. Verifica tu archivo .env")

#cargar ontología local
try:
    g.parse("ontologia/oficial.rdf", format="xml")
    print("Ontología cargada correctamente.")
    print("API Key cargada:", openai.api_key[:8] + "...")
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

    if not validar_sparql(query):
        return jsonify({"error": "Consulta SPARQL inválida. Revise la sintaxis."}), 400

    return ejecutar_sparql_aux(query, endpoint, lang)

@app.route("/preguntar", methods=["POST"])
def procesar_pregunta():
    data = request.get_json()
    pregunta = data.get("pregunta")
    endpoint = data.get("endpoint", "local")
    lang = data.get("lang", "es")

    if not pregunta:
        return jsonify({"error": "No se recibió ninguna pregunta"}), 400

    try:
        sparql = convertir_pregunta_a_sparql(pregunta, endpoint, lang)

        if not re.search(r"\b(select|ask|construct)\b", sparql, re.IGNORECASE):
            return jsonify({"error": "La consulta SPARQL generada no es válida (estructura incorrecta).", "consulta": sparql}), 500

        #solo validamos sintaxis con rdflib si es local
        if endpoint == "local" and not validar_sparql(sparql):
            return jsonify({"error": "La consulta SPARQL no pasó validación local.", "consulta": sparql}), 500

        return ejecutar_sparql_aux(sparql, endpoint, lang)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def ejecutar_sparql_aux(query, endpoint, lang):
    if endpoint == "dbpedia":
        propiedades_idioma = [
            "rdfs:label", "rdfs:comment", "dbo:abstract", "foaf:name", "skos:prefLabel"
        ]
        query = inyectar_filtros_idioma(query, lang, propiedades_idioma)

        print(f"\n[DBpedia] Consulta ({lang}):\n{query}\n")

        response = requests.get(
            "https://dbpedia.org/sparql",
            params={"query": query, "format": "application/sparql-results+json"}
        )

        if response.status_code != 200:
            return jsonify({
                "error": f"DBpedia respondió con error {response.status_code}",
                "detalle": response.text
            }), 500

        return jsonify(response.json())

    elif endpoint == "local":
        if g is None:
            return jsonify({"error": "Ontología no cargada."}), 500
        try:
            resultados = g.query(query)
            respuesta = [{str(var): str(fila[var]) for var in fila.labels} for fila in resultados]
            return jsonify({"resultados": respuesta, "total": len(respuesta)})
        except Exception as e:
            return jsonify({"error": f"Error al ejecutar consulta local: {str(e)}"}), 500

    else:
        return jsonify({"error": f"Fuente desconocida: {endpoint}"}), 400

def convertir_pregunta_a_sparql(pregunta, endpoint, lang):
    modelo = "gpt-4-1106-preview"
    endpoint = endpoint.lower()
    prefijo = "DBpedia" if endpoint == "dbpedia" else "la ontología local RDF"

    system_prompt = f"""
Eres un asistente experto en SPARQL. Tu tarea es convertir preguntas en lenguaje natural en consultas SPARQL.
Utiliza los prefijos correctos para {prefijo}. 
NO EXPLIQUES NADA. Devuelve SOLO la consulta SPARQL. No incluyas comentarios ni texto adicional.
"""

    user_prompt = f"Pregunta: {pregunta}\nIdioma: {lang}\nFuente: {endpoint}"

    try:
        response = client.chat.completions.create(
            model=modelo,
            messages=[
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_prompt.strip()}
            ],
            temperature=0.2,
            max_tokens=300
        )

        texto = response.choices[0].message.content.strip()

        # Limpiar formato innecesario (bloques markdown y etiquetas)
        texto = re.sub(r"^```sparql", "", texto, flags=re.IGNORECASE).strip()
        texto = re.sub(r"^sparql\s+", "", texto, flags=re.IGNORECASE).strip()
        texto = re.sub(r"```$", "", texto, flags=re.IGNORECASE).strip()
        texto = texto.replace("dbpedia-es:", "dbr:").replace("<http://es.dbpedia.org/resource/>", "<http://dbpedia.org/resource/>")


        return texto

    except Exception as e:
        raise Exception(f"Error API OpenAI: {str(e)}")

def extraer_vars_lingüisticas(consulta, propiedades):
    vars_detectadas = set()
    for prop in propiedades:
        patron = rf"{re.escape(prop)}\\s+\\?(\\w+)"
        matches = re.findall(patron, consulta)
        vars_detectadas.update(matches)
    return vars_detectadas

def inyectar_filtros_idioma(consulta, lang, propiedades):
    if "lang(" in consulta:
        return consulta

    vars_linguisticas = extraer_vars_lingüisticas(consulta, propiedades)
    if not vars_linguisticas:
        return consulta

    filtros = "".join(
        f"  FILTER(langMatches(lang(?{var}), \"{lang}\")) .\n" for var in vars_linguisticas
    )

    return consulta.replace("WHERE {", f"WHERE {{\n{filtros}")

def validar_sparql(query):
    try:
        parseQuery(query)
        return True
    except Exception as e:
        print(f"Error de sintaxis SPARQL: {e}")
        return False

@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", mensaje="Error interno del servidor."), 500

@app.errorhandler(404)
def not_found(error):
    return render_template("error.html", mensaje="Página no encontrada."), 404

if __name__ == "__main__":
    app.run(debug=True)
