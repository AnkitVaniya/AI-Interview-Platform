"""
Resume skill extraction.

Uses keyword/phrase matching against a known skills vocabulary rather than a
full NER model — this keeps the project runnable with zero extra downloads.
Swap this for a spaCy NER pipeline (fine-tuned on tech resumes) once you want
to catch skill mentions and phrasing this can't, e.g. "built REST APIs" implying
"API Design" without the literal word "API Design" appearing in the vocabulary.
"""
import re

SKILLS_VOCABULARY = [
    "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
    "react", "vue", "angular", "node.js", "express", "fastapi", "django", "flask",
    "spring boot", "mysql", "postgresql", "mongodb", "redis", "docker", "kubernetes",
    "aws", "gcp", "azure", "git", "graphql", "rest api", "microservices",
    "machine learning", "deep learning", "nlp", "pytorch", "tensorflow", "scikit-learn",
    "data structures", "algorithms", "sql", "html", "css", "tailwind",
    "ci/cd", "jenkins", "linux", "bash",
]

TOPIC_ALIASES = {
    "dynamic programming": "Dynamic Programming",
    "dp": "Dynamic Programming",
    "graph algorithms": "Graphs",
    "graphs": "Graphs",
    "trees": "Trees",
    "recursion": "Recursion",
    "backtracking": "Backtracking",
}


def extract_skills(resume_text: str) -> list[str]:
    text = resume_text.lower()
    found = set()
    for skill in SKILLS_VOCABULARY:
        # word-boundary match so "go" doesn't match inside "google"
        pattern = r"(?<![a-zA-Z0-9])" + re.escape(skill) + r"(?![a-zA-Z0-9])"
        if re.search(pattern, text):
            found.add(skill)
    return sorted(found)


def extract_known_topics(resume_text: str) -> list[str]:
    """Maps resume mentions to your platform's topic-graph node names, if any appear."""
    text = resume_text.lower()
    found = set()
    for alias, canonical in TOPIC_ALIASES.items():
        if alias in text:
            found.add(canonical)
    return sorted(found)
