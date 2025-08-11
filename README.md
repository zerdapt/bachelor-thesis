# Bachelor Thesis

### About the project
This thesis's purpose is to accompany my bachelor's thesis, titled "Ontology-based Modeling of Side Effects of Common Painkillers". 
For the technical part, a Python script was created to extract real-world data about drug adverse events from the openFDA API. The core of the project is the development of an OWL ontology that formally models common painkillers (like Ibuprofen and Metamizole), their side effects, and their varying regulatory approval statuses across different regions. The focus is on creating a machine-readable and queryable knowledge base that can answer complex questions for both clinical and legal domains. The ontology was developed using Protégé and is evaluated with SPARQL queries.

### Roadmap

- [x] Domain, scope and definition of competency questions
- [x] Selection of representative painkillers and their known side effects
- [x] Extracted adverse event data into two [CSV files](./data/raw/) of openFDA via [Python Script](./src/script.py)
- [x] Class and property modeling of the conceptual ontology model (domain, range and relationships)
- [x] Implementated the initial ontology schema in an [OWL file](./data/ontology/ontology_painkiller.rdf)
- [x] Validated the ontology for logical consistency, updating the [new OWL file](./data/ontology/ontology_painkiller_after_oops.rdfdata/)
- [x] Mapped the [clean CSV data](./data/processed/) to three [RDF turle files](./data/mapped/) using Ontotext Refine
- [x] Populated a GraphDB triple store and visualized the [final class hierarchy](./data/ontology/class-hierarchy-thesis-final.svg)
- [x] [Visualization](./data/ontology/ontology_visualization.svg) through WebVOWL of the new ontology schema 
- [x] [SPARQL queries](./queries/) in order to test the applicability and also look at the [results](./results/) as CSV files. 


#### Software

* **Protégé:** Version 5.6.5
* **Python:** Version 3.8+
* **pip:** Version 20.0+

### Getting Started

1.  **Clone the git repository**
    ```bash
    git clone https://github.com/zerdapt/bachelor-thesis
    ```

2.  **Navigate to the project directory**
    ```bash
    cd bachelor-thesis
    ```

3.  **Set up and activate the virtual environment**
    This creates an isolated environment for the project's dependencies. You only need to create it once.
    ```bash
    python -m venv venv
    ```
    Now, activate it. You need to do this every time you start working on the project.
    * **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    * **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install Python dependencies**
    With the virtual environment active, `pip` will now install the required packages into the correct isolated location.
    ```bash
    pip install -r requirements.txt
    ```

5.  **Run the data extraction script**
    This will generate the CSV files in the `/data` folder.
    ```bash
    python src/script.py
    ```

### Exploring the Ontology

After the setup is complete, you can open the ontology file located in the `/ontology` directory using Protégé in order to explore the class hierarchies, properties and individuals.


