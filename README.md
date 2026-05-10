# smartontology_220316009
smart ontology Knowledge Engineering and Ontologies – Project Idea 7: Academic Publication Knowledge Graph Mehmet Ensar DOLGUN - 220316009
--- Academic Publication Knowledge Graph ---

Project Overview

This project develops a **semantic knowledge graph** for the academic publication domain using OWL 2 ontology engineering and Semantic Web technologies. The system models scholarly publications, authors, research institutions, citation networks, research fields, and keywords — enabling complex semantic queries far beyond the capabilities of traditional bibliographic databases.

A key component of the project is the integration of a **Large Language Model (LLM)** to translate natural language questions into SPARQL queries, providing an intuitive interface for knowledge retrieval.

---

Domain & Scope

**Domain:** Academic Publications and Scholarly Communication  

**In Scope:**
- Academic publications (journal articles, conference papers)
- Authors and their institutional affiliations
- Citation relationships between publications
- Research fields and thematic keywords
- Publication venues (journals, conferences) with impact factors

**Out of Scope:**
- Book chapters, theses, preprints without peer review
- Full-text content and funding information
- Reviewer identities

---
**Changes in Version 2:**

ontology_akpkg_v2.ttl : Extended ontology with abstract property, symmetric collaboratesWith, foaf alignment
kg_construction_v2.py : Updated SPARQL queries to include abstract-based keyword search
llm_integration_v2.py : Updated system prompt with Phase 2 ontology schema
---

 Repository Structure

```
academic-publication-kg/
│
├── README.md                   # This file
│
├── ontology/
│   └── ontology_akpkg.ttl      # OWL 2 ontology in Turtle format (TBox + ABox)
│   └── ontology_akpkg_v2.ttl   # v2: Updated ontology with extended classes
├── docs/
│   ├── orsd-template-220316009.docx      # Ontology Requirements Specification Document (draft)
    ├── orsd-template-220316009_v2.docx   # version 2
    └── widoco/
      └── widoco_documentation.html
└── src/
    ├── kg_construction.py      # RDFlib-based knowledge graph construction & SPARQL queries  
    ├── kg_construction_v2.py   # Improved construction & queries
    ├── llm_integration.py      # LLM (Claude API) natural language to SPARQL pipeline
    └── llm_integration_v2.py   # Optimized NL-to-SPARQL pipeline
```

---

## 🧠 Ontology Design

The ontology is developed in **OWL 2 DL** and serialized in **Turtle (.ttl)** format.


Classes (TBox)

| Class | Superclass | Description |
|-------|-----------|-------------|
| Publication | owl:Thing | Any academic publication |
| Paper | Publication | A standalone research paper |
| JournalArticle | Paper | A paper published in a journal |
| ConferencePaper | Paper | A paper presented at a conference |
| Author | owl:Thing | A researcher who authored a publication |
| Institution | owl:Thing | A university or research organization |
| Venue | owl:Thing | Abstract publication outlet |
| Journal | Venue | A peer-reviewed periodic publication |
| Conference | Venue | A scholarly conference or workshop |
| ResearchField | owl:Thing | A scientific research domain |
| Keyword | owl:Thing | A thematic descriptor |


Object Properties

| Property | Domain | Range |
|----------|--------|-------|
| hasAuthor | Publication | Author |
| affiliatedWith | Author | Institution |
| publishedIn | Publication | Venue |
| cites | Publication | Publication |
| hasKeyword | Publication | Keyword |
| belongsToField | Publication | ResearchField |
| collaboratesWith | Author | Author *(Symmetric)* |


Data Properties

`title`, `year`, `doi`, `abstract`, `citationCount` — on Publication  
`name`, `orcid`, `hIndex` — on Author  
`institutionName`, `country` — on Institution  
`venueName` — on Venue  
`impactFactor` — on Journal

---

Competency Questions

The ontology is designed to answer the following questions:

1. What publications exist in the knowledge graph and what type are they?
2. Who are the authors of a given publication?
3. How many papers exist in each research field?
4. Which papers have the highest citation count (Top-N)?
5. Which authors have collaborated with each other?
6. Which papers cite a given target paper?
7. Which authors are affiliated with a specific institution?
8. How many papers are published in conferences vs. journals?
9. What NLP papers were published after 2016?
10. What is the average citation count per publication year?

---

Tools & Technologies

| Tool | Purpose |
|------|---------|
| OWL 2 DL / Turtle | Ontology language & serialization format |
| Protégé 5.x | Visual ontology editing |
| RDFlib (Python) | Knowledge graph construction & SPARQL querying |
| SPARQL 1.1 | Structured querying of the knowledge graph |
| SHACL | Data quality validation |
| GraphDB | Triple store deployment (planned) |
| Claude API | LLM-based NL-to-SPARQL translation |

---

Getting Started

### Requirements

```bash
pip install rdflib
```

Run the Knowledge Graph

```bash
cd src/
python kg_construction.py
```

This will load `ontology/ontology_akpkg.ttl`, execute all 10 SPARQL queries, and print results to the console.

Run the LLM Integration
Run the Latest Version (v2)
```bash
cd src/
python llm_integration_v2.py
```

> **Note:** Requires an Anthropic API key set in your environment.

---

Current Status

- [x] Domain selected: Academic Publication Knowledge Graph
- [x] ORSD specification document drafted (updated with version 2)
- [x] Initial OWL 2 ontology developed (11 classes, 7 object properties, 10 data properties)
- [x] ABox populated with 8 publications, 8 authors, 4 institutions, 7 venues
- [x] v2 Update: Ontology and python scripts updated with new features.
- [x] 10 SPARQL queries implemented and tested
- [x] SHACL validation shapes defined (5 shapes)
- [x] LLM integration module drafted
- [ ] GraphDB deployment
- [ ] Full-scale data ingestion from Semantic Scholar / OpenAlex API
- [ ] Final project report

---

References

- Berners-Lee, T., Hendler, J., & Lassila, O. (2001). The Semantic Web. *Scientific American*.
- Hitzler, P., Krotzsch, M., & Rudolph, S. (2009). *Foundations of Semantic Web Technologies*. CRC Press.
- McGuinness, D. L., & van Harmelen, F. (2004). OWL Web Ontology Language Overview. W3C Recommendation.
- Harris, S., & Seaborne, A. (2013). SPARQL 1.1 Query Language. W3C Recommendation.
- Knublauch, H., & Kontokostas, D. (2017). Shapes Constraint Language (SHACL). W3C Recommendation.

---
