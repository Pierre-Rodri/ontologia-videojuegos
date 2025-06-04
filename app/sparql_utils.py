import re
import requests
from flask import jsonify
from rdflib.plugins.sparql.parser import parseQuery

def validar_sparql(query):
    try:
        parseQuery(query)
        return True
    except Exception as e:
        print(f"Error de sintaxis SPARQL: {e}")
        return False

def ejecutar_sparql(query, endpoint, lang, g=None):
    if endpoint == "dbpedia":
        propiedades_idioma = [
            "rdfs:label", "rdfs:comment", "dbo:abstract", "foaf:name", "skos:prefLabel"
        ]
        query = inyectar_filtros_idioma(query, lang, propiedades_idioma)

        response = requests.get(
            "https://dbpedia.org/sparql",
            params={"query": query, "format": "application/sparql-results+json"}
        )

        if response.status_code != 200:
            return jsonify({"error": f"DBpedia respondió con error {response.status_code}"}), 500

        json_result = response.json()
        bindings = json_result.get("results", {}).get("bindings", [])
        procesados = []

        for fila in bindings:
            item = {}
            for var, val in fila.items():
                valor = val.get("value", "")
                tipo = val.get("type", "")

                if tipo == "uri":
                    item[var] = valor.split("/")[-1].replace("_", " ")
                elif tipo == "literal":
                    item[var] = valor
                else:
                    item[var] = valor
            procesados.append(item)

        return jsonify({
            "resultados": procesados,
            "total": len(procesados)
        })

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

def extraer_vars_lingüisticas(consulta, propiedades):
    vars_detectadas = set()
    for prop in propiedades:
        patron = rf"{re.escape(prop)}\\s+\\?(\\w+)"
        matches = re.findall(patron, consulta)
        vars_detectadas.update(matches)
    return vars_detectadas
