"""
LLM Integration Module - Natural Language to SPARQL
Translates user questions to SPARQL queries using Claude API.
"""

import json
import urllib.request
import urllib.error

ONTOLOGY_CONTEXT = """
You are an expert in SPARQL and ontologies.
The knowledge graph uses this ontology:

PREFIX akp: <http://www.akpkg.org/ontology#>

CLASSES: Publication, Paper, JournalArticle, ConferencePaper, Author,
         Institution, Venue, Journal, Conference, ResearchField, Keyword

OBJECT PROPERTIES:
  hasAuthor       (Publication -> Author)
  affiliatedWith  (Author -> Institution)
  publishedIn     (Publication -> Venue)
  cites           (Publication -> Publication)
  hasKeyword      (Publication -> Keyword)
  belongsToField  (Publication -> ResearchField)
  collaboratesWith (Author -> Author)  [Symmetric]

DATA PROPERTIES:
  title, year, doi, abstract, citationCount  (on Publication)
  name, orcid, hIndex                        (on Author)
  institutionName, country                   (on Institution)
  venueName                                  (on Venue)
  impactFactor                               (on Journal)

Instructions:
- Respond ONLY with a valid SPARQL SELECT query.
- Do NOT include any explanation or markdown code fences.
- Always include the PREFIX declarations.
- Use rdfs:label for ResearchField and Keyword labels.
- If the question cannot be answered, respond with: UNSUPPORTED
"""

def nl_to_sparql(natural_question: str) -> str:
    """Send a natural language question to Claude and get a SPARQL query."""
    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 1000,
        "system": ONTOLOGY_CONTEXT,
        "messages": [
            {"role": "user", "content": f"Convert this question to SPARQL:\n{natural_question}"}
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
            return data["content"][0]["text"].strip()
    except urllib.error.HTTPError as e:
        return f"API Error: {e.code} - {e.read().decode()}"

def demo():
    """Run example NL→SPARQL translations (requires API key in environment)."""
    questions = [
        "Who are the authors of 'Attention Is All You Need'?",
        "Which papers were published after 2016 in the NLP field?",
        "What is the average citation count grouped by year?",
        "Which authors have collaborated with Yoshua Bengio?",
        "List all journals and their impact factors.",
    ]

    for q in questions:
        print(f"\n[Question] {q}")
        sparql = nl_to_sparql(q)
        print(f"[SPARQL]\n{sparql}")
        print("-" * 60)

if __name__ == "__main__":
    demo()
