"""
Academic Publication Knowledge Graph — kg_construction.py
Version: 2.0
Phase 2 updates:
  - Loads ontology_akpkg_v2.ttl (abstract property, new keywords, new citation edge)
  - Added CQ11: keyword search inside abstract text
  - Added CQ12: average citation count grouped by field (basis for future prediction)
  - Added summary statistics output
"""

from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF, RDFS, OWL, XSD

AKP = Namespace("http://www.akpkg.org/ontology#")

# ── Graph loader ─────────────────────────────────────────────────────────────

def build_graph(ttl_path: str) -> Graph:
    g = Graph()
    g.parse(ttl_path, format="turtle")
    g.bind("akp", AKP)
    print(f"  Loaded: {ttl_path}")
    print(f"  Triples: {len(g)}\n")
    return g

# ── CQ1: All publications with type and year ─────────────────────────────────

def cq1_all_publications(g: Graph):
    q = """
    PREFIX akp:  <http://www.akpkg.org/ontology#>
    PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?title ?year ?type
    WHERE {
        ?paper rdf:type ?type .
        ?paper akp:title ?title .
        ?paper akp:year  ?year .
        FILTER(?type != owl:NamedIndividual)
    }
    ORDER BY DESC(?year)
    """
    return g.query(q)

# ── CQ2: Authors of a given paper ────────────────────────────────────────────

def cq2_authors_of_paper(g: Graph, paper_title: str):
    q = f"""
    PREFIX akp: <http://www.akpkg.org/ontology#>
    SELECT ?authorName
    WHERE {{
        ?paper akp:title "{paper_title}" .
        ?paper akp:hasAuthor ?author .
        ?author akp:name ?authorName .
    }}
    """
    return g.query(q)

# ── CQ3: Paper count per research field ──────────────────────────────────────

def cq3_papers_per_field(g: Graph):
    q = """
    PREFIX akp:  <http://www.akpkg.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?fieldLabel (COUNT(?paper) AS ?count)
    WHERE {
        ?paper akp:belongsToField ?field .
        ?field rdfs:label ?fieldLabel .
    }
    GROUP BY ?fieldLabel
    ORDER BY DESC(?count)
    """
    return g.query(q)

# ── CQ4: Top-N most cited papers ─────────────────────────────────────────────

def cq4_top_cited(g: Graph, n: int = 5):
    q = f"""
    PREFIX akp: <http://www.akpkg.org/ontology#>
    SELECT ?title ?citationCount
    WHERE {{
        ?paper akp:title ?title .
        ?paper akp:citationCount ?citationCount .
    }}
    ORDER BY DESC(?citationCount)
    LIMIT {n}
    """
    return g.query(q)

# ── CQ5: Author collaborations ───────────────────────────────────────────────

def cq5_collaborations(g: Graph):
    q = """
    PREFIX akp: <http://www.akpkg.org/ontology#>
    SELECT DISTINCT ?name1 ?name2
    WHERE {
        ?a1 akp:collaboratesWith ?a2 .
        ?a1 akp:name ?name1 .
        ?a2 akp:name ?name2 .
        FILTER(?name1 < ?name2)
    }
    ORDER BY ?name1
    """
    return g.query(q)

# ── CQ6: Papers that cite a given paper ──────────────────────────────────────

def cq6_citing_papers(g: Graph, target_title: str):
    q = f"""
    PREFIX akp: <http://www.akpkg.org/ontology#>
    SELECT ?citingTitle ?year
    WHERE {{
        ?target akp:title "{target_title}" .
        ?citing akp:cites ?target .
        ?citing akp:title ?citingTitle .
        ?citing akp:year  ?year .
    }}
    ORDER BY ?year
    """
    return g.query(q)

# ── CQ7: Authors by institution ──────────────────────────────────────────────

def cq7_authors_by_institution(g: Graph, inst_name: str):
    q = f"""
    PREFIX akp: <http://www.akpkg.org/ontology#>
    SELECT ?authorName ?hIndex
    WHERE {{
        ?author akp:name ?authorName .
        ?author akp:affiliatedWith ?inst .
        ?inst akp:institutionName "{inst_name}" .
        OPTIONAL {{ ?author akp:hIndex ?hIndex }}
    }}
    ORDER BY DESC(?hIndex)
    """
    return g.query(q)

# ── CQ8: Conference vs journal count ─────────────────────────────────────────

def cq8_venue_type_count(g: Graph):
    q = """
    PREFIX akp: <http://www.akpkg.org/ontology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?venueType (COUNT(?paper) AS ?count)
    WHERE {
        { ?paper rdf:type akp:ConferencePaper . BIND("Conference" AS ?venueType) }
        UNION
        { ?paper rdf:type akp:JournalArticle . BIND("Journal" AS ?venueType) }
    }
    GROUP BY ?venueType
    """
    return g.query(q)

# ── CQ9: NLP papers after a given year ───────────────────────────────────────

def cq9_nlp_papers_after(g: Graph, after_year: int = 2016):
    q = f"""
    PREFIX akp:  <http://www.akpkg.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?title ?year
    WHERE {{
        ?paper akp:belongsToField ?field .
        ?field rdfs:label "Natural Language Processing" .
        ?paper akp:title ?title .
        ?paper akp:year  ?year .
        FILTER(?year > {after_year})
    }}
    ORDER BY DESC(?year)
    """
    return g.query(q)

# ── CQ10: Average citation count per year ────────────────────────────────────

def cq10_avg_citations_by_year(g: Graph):
    q = """
    PREFIX akp: <http://www.akpkg.org/ontology#>
    SELECT ?year (AVG(?cit) AS ?avgCit) (COUNT(?p) AS ?numPapers)
    WHERE {
        ?p akp:year ?year .
        ?p akp:citationCount ?cit .
    }
    GROUP BY ?year
    ORDER BY ?year
    """
    return g.query(q)

# ── CQ11 [v2]: Papers containing a keyword in their abstract ─────────────────

def cq11_abstract_keyword_search(g: Graph, keyword: str):
    q = f"""
    PREFIX akp: <http://www.akpkg.org/ontology#>
    SELECT ?title ?year
    WHERE {{
        ?paper akp:title    ?title .
        ?paper akp:year     ?year .
        ?paper akp:abstract ?abstract .
        FILTER(CONTAINS(LCASE(?abstract), LCASE("{keyword}")))
    }}
    ORDER BY DESC(?year)
    """
    return g.query(q)

# ── CQ12 [v2]: Average citation count per research field ─────────────────────

def cq12_avg_citations_by_field(g: Graph):
    q = """
    PREFIX akp:  <http://www.akpkg.org/ontology#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT ?fieldLabel (AVG(?cit) AS ?avgCit) (COUNT(?p) AS ?numPapers)
    WHERE {
        ?p akp:belongsToField ?field .
        ?p akp:citationCount  ?cit .
        ?field rdfs:label ?fieldLabel .
    }
    GROUP BY ?fieldLabel
    ORDER BY DESC(?avgCit)
    """
    return g.query(q)

# ── Main ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import os

    # Try v2 first, fall back to v1
    ttl = "ontology/ontology_akpkg_v2.ttl"
    if not os.path.exists(ttl):
        ttl = "ontology/ontology_akpkg.ttl"

    print("=" * 60)
    print("Academic Publication Knowledge Graph — v2.0")
    print("=" * 60)

    g = build_graph(ttl)

    print("── CQ1: All Publications ──────────────────────────────────")
    for r in cq1_all_publications(g):
        t = str(r.type).split("#")[-1]
        print(f"  [{t}] {r.title} ({r.year})")

    print("\n── CQ2: Authors of 'Attention Is All You Need' ────────────")
    for r in cq2_authors_of_paper(g, "Attention Is All You Need"):
        print(f"  {r.authorName}")

    print("\n── CQ3: Papers per Research Field ─────────────────────────")
    for r in cq3_papers_per_field(g):
        print(f"  {r.fieldLabel}: {int(r.count)} paper(s)")

    print("\n── CQ4: Top 5 Most Cited Papers ───────────────────────────")
    for r in cq4_top_cited(g, 5):
        print(f"  {r.title} — {r.citationCount} citations")

    print("\n── CQ5: Author Collaborations ─────────────────────────────")
    for r in cq5_collaborations(g):
        print(f"  {r.name1}  ↔  {r.name2}")

    print("\n── CQ6: Papers Citing 'Attention Is All You Need' ─────────")
    for r in cq6_citing_papers(g, "Attention Is All You Need"):
        print(f"  {r.citingTitle} ({r.year})")

    print("\n── CQ7: Authors at Stanford University ────────────────────")
    for r in cq7_authors_by_institution(g, "Stanford University"):
        print(f"  {r.authorName} (h={r.hIndex})")

    print("\n── CQ8: Conference vs Journal Paper Count ──────────────────")
    for r in cq8_venue_type_count(g):
        print(f"  {r.venueType}: {int(r.count)}")

    print("\n── CQ9: NLP Papers Published After 2016 ───────────────────")
    for r in cq9_nlp_papers_after(g, 2016):
        print(f"  {r.title} ({r.year})")

    print("\n── CQ10: Average Citations by Year ────────────────────────")
    for r in cq10_avg_citations_by_year(g):
        print(f"  {r.year}: avg={float(r.avgCit):,.0f}  papers={r.numPapers}")

    print("\n── CQ11 [v2]: Abstract Search — 'attention' ───────────────")
    for r in cq11_abstract_keyword_search(g, "attention"):
        print(f"  {r.title} ({r.year})")

    print("\n── CQ12 [v2]: Average Citations by Research Field ──────────")
    for r in cq12_avg_citations_by_field(g):
        print(f"  {r.fieldLabel}: avg={float(r.avgCit):,.0f}  papers={r.numPapers}")

    print("\n── Knowledge Graph Statistics ─────────────────────────────")
    print(f"  Total triples    : {len(g)}")
    classes    = set(g.subjects(RDF.type, OWL.Class))
    obj_props  = set(g.subjects(RDF.type, OWL.ObjectProperty))
    data_props = set(g.subjects(RDF.type, OWL.DatatypeProperty))
    print(f"  OWL Classes      : {len(classes)}")
    print(f"  Object Properties: {len(obj_props)}")
    print(f"  Data Properties  : {len(data_props)}")
    print("=" * 60)
