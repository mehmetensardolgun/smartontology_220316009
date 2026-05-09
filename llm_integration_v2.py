"""
Academic Publication Knowledge Graph — llm_integration.py
Version: 1.1
Phase 2 updates:
  - System prompt updated with v2 ontology schema (abstract property, new keywords)
  - Added CQ11 and CQ12 examples to the demo
  - Added intent classification hint to route aggregation vs retrieval queries
  - Added basic SPARQL syntax validation before execution
"""

import json
import urllib.request
import urllib.error
import re

# ── Ontology context for the LLM ─────────────────────────────────────────────

ONTOLOGY_CONTEXT = """
You are an expert in SPARQL and OWL ontologies.
The knowledge graph uses the following ontology (Version 2.0):

PREFIX akp:  <http://www.akpkg.org/ontology#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf:  <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

CLASSES:
  akp:Publication   — any academic publication
  akp:Paper         — subClassOf Publication
  akp:JournalArticle — subClassOf Paper
  akp:ConferencePaper — subClassOf Paper
  akp:Author        — a researcher
  akp:Institution   — a university or research organization
  akp:Venue         — abstract publication outlet
  akp:Journal       — subClassOf Venue (has impactFactor)
  akp:Conference    — subClassOf Venue
  akp:ResearchField — a scientific domain
  akp:Keyword       — a thematic descriptor

OBJECT PROPERTIES:
  akp:hasAuthor        (Publication → Author)
  akp:affiliatedWith   (Author → Institution)
  akp:publishedIn      (Publication → Venue)
  akp:cites            (Publication → Publication)
  akp:hasKeyword       (Publication → Keyword)
  akp:belongsToField   (Publication → ResearchField)
  akp:collaboratesWith (Author → Author)  [owl:SymmetricProperty]

DATA PROPERTIES on Publication:
  akp:title           xsd:string
  akp:year            xsd:integer
  akp:doi             xsd:string
  akp:abstract        xsd:string   ← [v2] use CONTAINS(LCASE(?abstract), ...) for text search
  akp:citationCount   xsd:integer

DATA PROPERTIES on Author:
  akp:name            xsd:string
  akp:orcid           xsd:string
  akp:hIndex          xsd:integer

DATA PROPERTIES on Institution:
  akp:institutionName xsd:string
  akp:country         xsd:string

DATA PROPERTIES on Venue/Journal:
  akp:venueName       xsd:string
  akp:impactFactor    xsd:decimal

IMPORTANT RULES:
1. Respond ONLY with a valid SPARQL SELECT query.
2. Do NOT include markdown code fences, explanations, or preamble.
3. Always include all required PREFIX declarations at the top.
4. Use rdfs:label for ResearchField and Keyword labels (e.g., "Natural Language Processing").
5. For abstract text search, use: FILTER(CONTAINS(LCASE(?abstract), LCASE("keyword")))
6. For aggregation queries use COUNT, AVG, GROUP BY as appropriate.
7. collaboratesWith is symmetric — asserting one direction is sufficient.
8. If the question cannot be answered with the ontology, respond with exactly: UNSUPPORTED
"""

# ── Intent classifier ─────────────────────────────────────────────────────────

def classify_intent(question: str) -> str:
    """
    [v2] Simple keyword-based intent classifier.
    Routes to 'aggregation' or 'retrieval' to hint the LLM.
    """
    agg_keywords = ["how many", "count", "average", "avg", "total",
                    "most cited", "kaç", "ortalama", "toplam", "en çok"]
    q_lower = question.lower()
    for kw in agg_keywords:
        if kw in q_lower:
            return "aggregation"
    return "retrieval"

# ── SPARQL syntax validator ───────────────────────────────────────────────────

def validate_sparql(sparql: str) -> bool:
    """
    [v2] Basic structural validation before execution.
    Returns True if the query looks syntactically plausible.
    """
    if sparql.strip() == "UNSUPPORTED":
        return False
    required = ["SELECT", "WHERE", "{", "}"]
    return all(kw in sparql.upper() for kw in required)

# ── NL → SPARQL translation ───────────────────────────────────────────────────

def nl_to_sparql(natural_question: str) -> str:
    """
    Sends a natural language question to Claude and returns a SPARQL query.
    Requires an Anthropic API key (handled by the proxy — no key needed in code).
    """
    intent = classify_intent(natural_question)
    intent_hint = (
        "This appears to be an AGGREGATION query — use COUNT, AVG, or GROUP BY."
        if intent == "aggregation"
        else "This appears to be a RETRIEVAL query — return individual instances."
    )

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "system": ONTOLOGY_CONTEXT,
        "messages": [
            {
                "role": "user",
                "content": (
                    f"Intent hint: {intent_hint}\n\n"
                    f"Convert this question to a SPARQL query:\n{natural_question}"
                )
            }
        ]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read())
            sparql = data["content"][0]["text"].strip()
            return sparql
    except urllib.error.HTTPError as e:
        return f"API Error {e.code}: {e.read().decode()}"
    except Exception as e:
        return f"Error: {e}"

# ── Execute against RDFlib graph ──────────────────────────────────────────────

def execute_query(sparql: str, g):
    """
    [v2] Executes a validated SPARQL query against an rdflib Graph.
    Returns list of result rows or an error message.
    """
    if not validate_sparql(sparql):
        return None, "Invalid or unsupported SPARQL query."
    try:
        results = list(g.query(sparql))
        return results, None
    except Exception as e:
        return None, f"Query execution error: {e}"

# ── Demo ─────────────────────────────────────────────────────────────────────

def demo():
    """
    Run example NL→SPARQL translations.
    API key must be set in the environment or handled by a proxy.
    """
    questions = [
        # CQ1–CQ10 style
        "Who are the authors of 'Attention Is All You Need'?",
        "Which papers were published after 2016 in the NLP field?",
        "How many papers exist in each research field?",
        "Which authors have collaborated with Yoshua Bengio?",
        # CQ11–CQ12 style [v2]
        "Which papers mention 'attention' in their abstract?",
        "What is the average citation count per research field?",
    ]

    for q in questions:
        intent = classify_intent(q)
        print(f"\n[Question]  {q}")
        print(f"[Intent]    {intent}")
        sparql = nl_to_sparql(q)
        valid = validate_sparql(sparql)
        print(f"[Valid]     {valid}")
        print(f"[SPARQL]\n{sparql}")
        print("-" * 60)

if __name__ == "__main__":
    demo()
