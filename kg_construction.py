"""
Academic Publication Knowledge Graph - Construction Script
Uses RDFlib to build and query the knowledge graph from the ontology.
"""

from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, OWL, XSD
import json

AKP = Namespace("http://www.akpkg.org/ontology#")

def build_graph(ttl_path: str) -> Graph:
    g = Graph()
    g.parse(ttl_path, format="turtle")
    g.bind("akp", AKP)
    return g

def query_all_publications(g: Graph):
    query = """
    PREFIX akp: <http://www.akpkg.org/ontology#>
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
    return g.query(query)

def query_citations_per_field(g: Graph):
    query = """
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
    return g.query(query)

def query_top_cited(g: Graph, n: int = 5):
    query = """
    PREFIX akp: <http://www.akpkg.org/ontology#>
    SELECT ?title ?citationCount
    WHERE {
      ?paper akp:title ?title .
      ?paper akp:citationCount ?citationCount .
    }
    ORDER BY DESC(?citationCount)
    LIMIT %d
    """ % n
    return g.query(query)

def query_collaborations(g: Graph):
    query = """
    PREFIX akp: <http://www.akpkg.org/ontology#>
    SELECT DISTINCT ?name1 ?name2
    WHERE {
      ?a1 akp:collaboratesWith ?a2 .
      ?a1 akp:name ?name1 .
      ?a2 akp:name ?name2 .
      FILTER(?name1 < ?name2)
    }
    """
    return g.query(query)

def query_avg_citations_by_year(g: Graph):
    query = """
    PREFIX akp: <http://www.akpkg.org/ontology#>
    SELECT ?year (AVG(?cit) AS ?avgCit) (COUNT(?p) AS ?num)
    WHERE {
      ?p akp:year ?year .
      ?p akp:citationCount ?cit .
    }
    GROUP BY ?year
    ORDER BY ?year
    """
    return g.query(query)

if __name__ == "__main__":
    print("Loading knowledge graph...")
    g = build_graph("ontology.ttl")
    print(f"  Triples loaded: {len(g)}\n")

    print("=== All Publications ===")
    for row in query_all_publications(g):
        type_local = str(row.type).split("#")[-1]
        print(f"  [{type_local}] {row.title} ({row.year})")

    print("\n=== Papers per Research Field ===")
    for row in query_citations_per_field(g):
        print(f"  {row.fieldLabel}: {row.count} paper(s)")

    print("\n=== Top 5 Most Cited Papers ===")
    for row in query_top_cited(g, 5):
        print(f"  {row.title} — {row.citationCount} citations")

    print("\n=== Author Collaborations ===")
    for row in query_collaborations(g):
        print(f"  {row.name1}  ↔  {row.name2}")

    print("\n=== Average Citations by Year ===")
    for row in query_avg_citations_by_year(g):
        print(f"  {row.year}: avg={float(row.avgCit):.0f}, papers={row.num}")

    print("\nKnowledge Graph summary:")
    print(f"  Total triples : {len(g)}")
    classes = set(g.subjects(RDF.type, OWL.Class))
    print(f"  OWL Classes   : {len(classes)}")
    instances = set(s for s, p, o in g if p == RDF.type and o != OWL.Class
                    and o != OWL.ObjectProperty and o != OWL.DatatypeProperty
                    and o != OWL.Ontology and o != OWL.SymmetricProperty)
    print(f"  Instances     : {len(instances)}")
