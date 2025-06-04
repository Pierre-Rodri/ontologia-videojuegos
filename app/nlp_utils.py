
import openai
import re

def convertir_pregunta_a_sparql(pregunta, endpoint, lang):
    modelo = "gpt-4-1106-preview"
    prefijo = "DBpedia" if endpoint == "dbpedia" else "la ontología local RDF"

    system_prompt = f"""
Eres un experto en ontologías y consultas SPARQL. Convierte preguntas en lenguaje natural en consultas SPARQL utilizando DBpedia como fuente si el endpoint es DBpedia.

Reglas:
1. Usa siempre los prefijos: dbo, dbr, rdfs.
2. Incluye ?label con rdfs:label cuando devuelvas URIs.
3. Agrega un filtro de idioma con FILTER(langMatches(lang(?label), "{lang}"))
4. NO devuelvas texto adicional, SOLO la consulta SPARQL sin bloques ```sparql.
"""

    user_prompt = f"Pregunta: {pregunta}\nIdioma: {lang}\nFuente: {endpoint}"

    try:
        response = openai.Completion.create(
            model=modelo,
            prompt=system_prompt + user_prompt,
            temperature=0.2,
            max_tokens=300
        )

        texto = response.choices[0].text.strip()

        # Limpiar el formato innecesario
        texto = re.sub(r"^```sparql", "", texto, flags=re.IGNORECASE).strip()
        texto = re.sub(r"^sparql\s+", "", texto, flags=re.IGNORECASE).strip()
        texto = re.sub(r"```$", "", texto, flags=re.IGNORECASE).strip()
        texto = texto.replace("dbpedia-es:", "dbr:").replace("<http://es.dbpedia.org/resource/>", "<http://dbpedia.org/resource/>")

        return texto

    except Exception as e:
        raise Exception(f"Error API OpenAI: {str(e)}")
