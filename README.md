#Proyecto: Ontología de Videojuegos

Este proyecto consiste en una aplicación web que utiliza una ontología RDF para representar y consultar información sobre videojuegos. 
Se implementa una API y una interfaz web usando Flask, junto con herramientas de representación semántica como RDFLib.

## Herramientas y Tecnologías Utilizadas

| Herramienta         | Función                                                                 |
|---------------------|-------------------------------------------------------------------------|
| **Python 3.13**      | Lenguaje de programación principal                                      |
| **Flask**            | Framework web para crear la API y la interfaz                          |
| **rdflib**           | Librería Python para trabajar con RDF y consultas SPARQL               |
| **owlready2**        | Librería de razonamiento OWL (opcional en este proyecto)               |
| **HTML / CSS / JS**  | Tecnologías para construir la interfaz web del cliente                 |
| **Ontología RDF**    | Archivo `.rdf` generado con Protégé para el dominio de Videojuegos     |

---

## Requisitos e Instalación

1. Clona este repositorio:
   ```bash
   git clone <URL-del-repositorio>
   cd ontologia-videojuegos
2. Crea un entorno virtual:
   ```bash
   python - m venv venv
3. Instala las dependencias:
   ```bash
   pip install flask
   pip install rdflib
   pip install requests
4. Ejecutar el proyecto
   ```bash
   py app.py
   
