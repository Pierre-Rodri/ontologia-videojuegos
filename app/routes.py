# Manejo de solicitudes
from flask import Flask, request, jsonify, render_template
from app.sparql_utils import ejecutar_sparql, validar_sparql
from app.nlp_utils import convertir_pregunta_a_sparql
from app.keyword_utils import buscar_por_keyword
from app.config import cargar_ontologia
import openai
import os

app = Flask(__name__)
g = cargar_ontologia()

openai.api_key = os.getenv("API_key")
client = openai.OpenAI(api_key=openai.api_key)

if not openai.api_key:
    raise ValueError("No se encontró la clave API de OpenAI. Verifica tu archivo .env")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/sparql", methods=["POST"])
def ejecutar_sparql_query():
    data = request.get_json()
    query = data.get('query')
    endpoint = data.get('endpoint', 'local')
    lang = data.get('lang', 'en')

    if not query:
        return jsonify({"error": "Falta el campo 'query'"}), 400

    if not validar_sparql(query):
        return jsonify({"error": "Consulta SPARQL inválida. Revise la sintaxis."}), 400

    return ejecutar_sparql(query, endpoint, lang, g)

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
        if not validar_sparql(sparql):
            return jsonify({"error": "La consulta SPARQL generada no es válida."}), 500
        return ejecutar_sparql(sparql, endpoint, lang)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/keyword", methods=["POST"])
def buscar_por_keyword_route():
    data = request.get_json()
    keyword = data.get("keyword", "").strip()
    endpoint = data.get("endpoint", "local")
    lang = data.get("lang", "es")
    
    if not keyword:
        return jsonify({"error": "No se proporcionó palabra clave."}), 400

    return buscar_por_keyword(keyword, endpoint, lang)
