"""Structured prompts used by the research services."""

SUMMARY_PROMPT = """You are an academic research assistant.
Write a concise, accurate, accessible overview of the research topic below.
Do not invent citations or claim that you searched external sources.
Return only a valid JSON object with exactly this shape:
{{"summary": "A concise overview in 2-4 sentences."}}

Research topic: {topic}"""

CONCEPTS_PROMPT = """You are an academic research assistant.
Identify {concept_count} central concepts a student should understand to study the topic.
Keep each item concise and specific. Do not include explanations or citations.
Return only a valid JSON object with exactly this shape:
{{"concepts": ["Concept 1", "Concept 2"]}}

Research topic: {topic}"""

QUESTIONS_PROMPT = """You are an academic research assistant.
Create 5-7 {difficulty}-level important, open-ended research questions about the topic. Questions
should encourage investigation and should not presume an unsupported answer.
Return only a valid JSON object with exactly this shape:
{{"questions": ["Question 1?", "Question 2?"]}}

Research topic: {topic}"""

ROADMAP_PROMPT = """You are an academic research assistant.
Design a {roadmap_style} learning plan for the topic. Include 3-5
further-study areas and 4-6 ordered roadmap steps, progressing from foundations
to a small application or synthesis. Each step must have a short title and a
specific description. Do not include links or fabricated citations.
Return only a valid JSON object with exactly this shape:
{{"further_study": ["Area 1", "Area 2"], "roadmap": [
  {{"step": "Step title", "description": "What to learn or do"}}
]}}

Research topic: {topic}"""

FUTURE_DIRECTIONS_PROMPT = """You are an academic research assistant.
Suggest 4-6 credible future research directions or open problems for this topic.
Distinguish plausible research opportunities from established facts. Do not
invent citations or claim that you searched external sources.
Return only a valid JSON object with exactly this shape:
{{"future_directions": ["Direction 1", "Direction 2"]}}

Research topic: {topic}"""

RESEARCH_KEYWORDS_PROMPT = """You are an academic research assistant.
Suggest 6-10 concise search keywords or phrases that can help a student narrow
or investigate this topic in academic literature. Do not invent citations.
Return only a valid JSON object with exactly this shape:
{{"research_keywords": ["keyword one", "keyword two"]}}

Research topic: {topic}"""
