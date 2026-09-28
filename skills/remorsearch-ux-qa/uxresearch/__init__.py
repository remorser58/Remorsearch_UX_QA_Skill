"""Honest public-page reader and research tools for the research mode.

Standard library only. Site knowledge (official routes, mobile twins, login
hosts) lives in `uxresearch/data/*.json`, never in this package's code.
"""

VERSION = "0.1.0"
RULES_VERSION = "ux-research-rules.1"
PROJECT_URL = "https://github.com/remorser58/ux-research-qa-skills"
ROBOTS_TOKEN = "RemorsearchUXQA"
USER_AGENT = f"{ROBOTS_TOKEN}/{VERSION} (+{PROJECT_URL}; read-only UX research)"
