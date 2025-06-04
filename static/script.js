const resultBox = document.getElementById("result");
const loader = document.getElementById("loader");

document.querySelectorAll(".collapsible").forEach(button => {
    button.addEventListener("click", () => {
    const expanded = button.getAttribute("aria-expanded") === "true";
    button.setAttribute("aria-expanded", !expanded);
    const contentId = button.getAttribute("aria-controls");
    const content = document.getElementById(contentId);
    if (content) {
        content.style.display = expanded ? "none" : "block";
    }
    });
});

document.getElementById("sparqlForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const query = document.getElementById("query").value;
    const endpoint = document.getElementById("endpoint").value;
    const idioma = document.getElementById("lang").value;

    if (!query.trim()) {
    alert(textos[lang.value]["alert_sparql"]);
    return;
    }

    loader.style.display = "block";
    resultBox.innerHTML = "";

    try {
    const res = await fetch("/sparql", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, endpoint, lang: idioma })
    });

    const data = await res.json();
    mostrarResultados(data);
    } catch {
    resultBox.textContent = textos[lang.value]["error_server"];
    } finally {
    loader.style.display = "none";
    }
});

document.getElementById("keywordForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const keyword = document.getElementById("keyword").value.trim();
    const endpoint = document.getElementById("keywordSource").value;
    const idioma = document.getElementById("lang").value;

    if (!keyword) {
    alert(textos[lang.value]["alert_keyword"]);
    return;
    }

    loader.style.display = "block";
    resultBox.innerHTML = "";

    try {
    const res = await fetch("/keyword", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ keyword, endpoint, lang: idioma })  // ✅ CORRECTO
    });

    const data = await res.json();
    mostrarResultados(data);
    } catch {
    resultBox.textContent = textos[lang.value]["error_server"];
    } finally {
    loader.style.display = "none";
    }
});


document.getElementById("nlpForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const pregunta = document.getElementById("pregunta").value.trim();
    const endpoint = document.getElementById("fuenteNLP").value;
    const idioma = document.getElementById("lang").value;

    if (!pregunta) {
    alert("Por favor, escribe una pregunta.");
    return;
    }

    loader.style.display = "block";
    resultBox.innerHTML = "";

    try {
    const res = await fetch("/preguntar", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pregunta, endpoint, lang: idioma })
    });

    const data = await res.json();
    mostrarResultados(data);
    } catch {
    resultBox.textContent = "Error al contactar el servidor.";
    } finally {
    loader.style.display = "none";
    }
});

function mostrarResultados(data) {
    const title = document.getElementById("resultTitle");
    const container = document.getElementById("result");
    const bindings = data.resultados || (data.results && data.results.bindings);

    container.innerHTML = "";

    if (bindings && bindings.length > 0) {
    // Comprobar si al menos un resultado tiene un idioma distinto al seleccionado
    let idiomaSeleccionado = lang.value;
    let contenidoOtroIdioma = false;
    bindings.forEach(row => {
        for (const key in row) {
        const valor = row[key];
        // Si es objeto con "xml:lang" y el idioma no coincide
        if (valor && valor['xml:lang'] && valor['xml:lang'] !== idiomaSeleccionado) {
            contenidoOtroIdioma = true;
        }
        }
    });

    if (contenidoOtroIdioma) {
        const advertencia = document.createElement("p");
        advertencia.style.color = "#cc6600";
        if (idiomaSeleccionado === "es") {
        advertencia.textContent = "⚠️ Algunas partes del contenido están en otro idioma.";
        } else if (idiomaSeleccionado === "en") {
        advertencia.textContent = "⚠️ Some content parts are in a different language.";
        } else if (idiomaSeleccionado === "fr") {
        advertencia.textContent = "⚠️ Certaines parties du contenu sont dans une autre langue.";
        } else if (idiomaSeleccionado === "ja") {
        advertencia.textContent = "⚠️ コンテンツの一部は別の言語で表示されています。";
        }
        resultBox.prepend(advertencia);
    }
    }

    if (bindings && bindings.length > 0) {
    title.textContent = `Resultados: ${bindings.length} encontrados`;
    title.style.display = "block";

    const table = document.createElement("table");
    const thead = document.createElement("thead");
    const headerRow = document.createElement("tr");

    Object.keys(bindings[0]).forEach(key => {
        const th = document.createElement("th");
        th.textContent = key;
        headerRow.appendChild(th);
    });
    thead.appendChild(headerRow);
    table.appendChild(thead);

    const tbody = document.createElement("tbody");
    bindings.forEach(row => {
        const tr = document.createElement("tr");
        Object.values(row).forEach(cell => {
        const td = document.createElement("td");
        td.textContent = typeof cell === "object" ? cell.value : cell;
        tr.appendChild(td);
        });
        tbody.appendChild(tr);
    });
    table.appendChild(tbody);
    resultBox.appendChild(table);
    resultBox.scrollIntoView({ behavior: "smooth" });
    } else {
    title.textContent = "Resultados:";
    title.style.display = "block";
    container.textContent = textos[lang.value]["no_results"];
    title.scrollIntoView({ behavior: "smooth" });
    }
}

const lang = document.getElementById("lang");
const textos = {
    es: {
    "alert_sparql": "Por favor, escribe una consulta SPARQL.",
    "alert_keyword": "Por favor, escribe una palabra clave.",
    "error_server": "Error inesperado al contactar el servidor.",
    "no_results": "No se encontraron resultados.",
    "titulo": "Buscador Semántico de Videojuegos",
    "tituloSparql": "Consulta SPARQL avanzada",
    "labelFuente": "Selecciona la fuente:",
    "labelConsulta": "Consulta SPARQL:",
    "btnEjecutar": "Ejecutar",
    "tituloPalabra": "Búsqueda por palabra clave",
    "labelPalabra": "Ingresa una palabra clave:",
    "labelFuente2": "Selecciona la fuente:",
    "btnBuscar": "Buscar",
    "tituloPregunta": "Pregunta en lenguaje natural",
    "labelPregunta": "Escribe tu pregunta:",
    "fuenteNLP": "Selecciona la fuente:",
    "btnPregunta": "Buscar",
    },
    en: {
    "alert_sparql": "Please enter a SPARQL query.",
    "alert_keyword": "Please enter a keyword.",
    "error_server": "Unexpected error contacting the server.",
    "no_results": "No results found.",
    "titulo": "Semantic Video Game Search",
    "tituloSparql": "Advanced SPARQL Query",
    "labelFuente": "Select source:",
    "labelConsulta": "SPARQL Query:",
    "btnEjecutar": "Execute",
    "tituloPalabra": "Keyword Search",
    "labelPalabra": "Enter a keyword:",
    "labelFuente2": "Select source:",
    "btnBuscar": "Search",
    "tituloPregunta": "Natural Language Question",
    "labelPregunta": "Write your question:",
    "fuenteNLP": "Select source:",
    "btnPregunta": "Search",
    },
    fr: {
    "alert_sparql": "Veuillez saisir une requête SPARQL.",
    "alert_keyword": "Veuillez saisir un mot-clé.",
    "error_server": "Erreur inattendue lors de la connexion au serveur.",
    "no_results": "Aucun résultat trouvé.",
    "titulo": "Recherche Sémantique de Jeux Vidéo",
    "tituloSparql": "Requête SPARQL Avancée",
    "labelFuente": "Sélectionnez la source :",
    "labelConsulta": "Requête SPARQL :",
    "btnEjecutar": "Exécuter",
    "tituloPalabra": "Recherche par mot-clé",
    "labelPalabra": "Entrez un mot-clé :",
    "labelFuente2": "Sélectionnez la source :",
    "btnBuscar": "Rechercher",
    "tituloPregunta": "Question en langage naturel",
    "labelPregunta": "Écrivez votre question :",
    "fuenteNLP": "Sélectionnez la source :",
    "btnPregunta": "Consulter",
    },
    ja: {
    "alert_sparql": "SPARQLクエリを入力してください。",
    "alert_keyword": "キーワードを入力してください。",
    "error_server": "サーバーへの接続中に予期しないエラーが発生しました。",
    "no_results": "結果が見つかりませんでした。",
    "titulo": "セマンティックゲーム検索",
    "tituloSparql": "高度なSPARQLクエリ",
    "labelFuente": "ソースを選択：",
    "labelConsulta": "SPARQLクエリ：",
    "btnEjecutar": "実行",
    "tituloPalabra": "キーワード検索",
    "labelPalabra": "キーワードを入力：",
    "labelFuente2": "ソースを選択：",
    "btnBuscar": "検索",
    "tituloPregunta": "自然言語の質問",
    "labelPregunta": "質問を入力してください：",
    "fuenteNLP": "ソースを選択：",
    "btnPregunta": "問い合わせる",
    }
};

lang.addEventListener("change", () => {
    const t = textos[lang.value];
    document.getElementById("titulo").textContent = t.titulo;
    document.getElementById("tituloSparql").textContent = t.tituloSparql;
    document.getElementById("labelFuente").textContent = t.labelFuente;
    document.getElementById("labelConsulta").textContent = t.labelConsulta;
    document.getElementById("btnEjecutar").textContent = t.btnEjecutar;
    document.getElementById("tituloPalabra").textContent = t.tituloPalabra;
    document.getElementById("labelPalabra").textContent = t.labelPalabra;
    document.getElementById("labelFuente2").textContent = t.labelFuente2;
    document.getElementById("btnBuscar").textContent = t.btnBuscar;
    document.getElementById("tituloPregunta").textContent = t.tituloPregunta;
    document.getElementById("labelPregunta").textContent = t.labelPregunta;
    document.getElementById("labelFuenteNLP").textContent = t.fuenteNLP;
    document.getElementById("btnPregunta").textContent = t.btnPregunta;
});