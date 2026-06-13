"""
agent.py

The FitFindr planning loop. Orchestrates the three tools in response to a
natural language user query, passing state between them via a session dict.

Complete tools.py and test each tool in isolation before implementing this file.

Usage (once implemented):
    from agent import run_agent
    from utils.data_loader import get_example_wardrobe

    result = run_agent(
        query="vintage graphic tee under $30, size M",
        wardrobe=get_example_wardrobe(),
    )
    print(result["fit_card"])
    print(result["error"])   # None on success
"""

import re

from tools import create_fit_card, search_listings, suggest_outfit

# ── session state ─────────────────────────────────────────────────────────────

def _new_session(query: str, wardrobe: dict) -> dict:
    """
    Initialize and return a fresh session dict for one user interaction.

    The session dict is the single source of truth for everything that happens
    during a run — it stores the original query, parsed parameters, tool results,
    and any error that caused early termination.

    You may add fields to this dict as needed for your implementation.
    """
    return {
        "query": query,              # original user query
        "parsed": {},                # extracted description / size / max_price
        "search_results": [],        # list of matching listing dicts
        "selected_item": None,       # top result, passed into suggest_outfit
        "wardrobe": wardrobe,        # user's wardrobe dict
        "outfit_suggestion": None,   # string returned by suggest_outfit
        "fit_card": None,            # string returned by create_fit_card
        "error": None,               # set if the interaction ended early
    }


# ── planning loop ─────────────────────────────────────────────────────────────
_PRICE_PATTERN = re.compile(
    r"(?:under|below|less than|max|maximum|up to)\s*\$?\s*(\d+(?:\.\d+)?)",
    re.IGNORECASE,
)

_SIZE_PATTERN = re.compile(
    r"(?:size\s+|in\s+size\s+)([a-zA-Z0-9./-]+)",
    re.IGNORECASE,
)

_FILLER_PHRASES = [
    "i'm looking for",
    "im looking for",
    "i am looking for",
    "looking for",
    "what's out there",
    "whats out there",
    "how would i style it",
    "and how would i style it",
]


def _parse_query(query: str) -> dict:
    """
    Extract simple search parameters from the user's natural language query.

    This intentionally uses regex/string cleanup instead of an LLM so the
    planning loop is deterministic and easy to test.
    """
    raw_query = query or ""
    cleaned = raw_query.lower()

    max_price = None
    price_match = _PRICE_PATTERN.search(cleaned)
    if price_match:
        max_price = float(price_match.group(1))
        cleaned = _PRICE_PATTERN.sub("", cleaned)

    size = None
    size_match = _SIZE_PATTERN.search(cleaned)
    if size_match:
        size = size_match.group(1).strip().upper()
        cleaned = _SIZE_PATTERN.sub("", cleaned)

    for phrase in _FILLER_PHRASES:
        cleaned = cleaned.replace(phrase, "")

    cleaned = cleaned.replace("?", " ")
    cleaned = cleaned.replace(".", " ")
    cleaned = cleaned.replace(",", " ")
    cleaned = cleaned.replace("  ", " ")

    description = " ".join(cleaned.split()).strip()

    return {
        "description": description,
        "size": size,
        "max_price": max_price,
    }


def _is_error_text(value: str | None) -> bool:
    """Return True when a tool returned an error-like message string."""
    if not value or not value.strip():
        return True

    lowered = value.lower()
    return lowered.startswith("error:") or "couldn't" in lowered or "could not" in lowered

def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Main agent entry point. Runs the FitFindr planning loop for a single
    user interaction and returns the completed session dict.
    """
    session = _new_session(query, wardrobe)

    parsed = _parse_query(query)
    session["parsed"] = parsed

    description = parsed["description"]
    size = parsed["size"]
    max_price = parsed["max_price"]

    if not description:
        session["error"] = (
            "Please describe what kind of clothing item you want to search for."
        )
        return session

    search_results = search_listings(
        description=description,
        size=size,
        max_price=max_price,
    )
    session["search_results"] = search_results

    if not search_results:
        session["error"] = (
            "I couldn’t find any listings matching that search. Try raising your "
            "budget, removing the size filter, or using a broader keyword like "
            "'graphic tee'."
        )
        return session

    selected_item = search_results[0]
    session["selected_item"] = selected_item

    outfit_suggestion = suggest_outfit(
        new_item=selected_item,
        wardrobe=wardrobe,
    )
    session["outfit_suggestion"] = outfit_suggestion

    if _is_error_text(outfit_suggestion):
        session["error"] = (
            "I found a listing, but I could not create a usable outfit suggestion."
        )
        return session

    fit_card = create_fit_card(
        outfit=outfit_suggestion,
        new_item=selected_item,
    )
    session["fit_card"] = fit_card

    if _is_error_text(fit_card):
        session["error"] = (
            "I found the item and outfit idea, but I could not create a fit card."
        )
        return session

    return session


# ── CLI test ──────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

    print("=== Happy path: graphic tee ===\n")
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )
    if session["error"]:
        print(f"Error: {session['error']}")
    else:
        print(f"Found: {session['selected_item']['title']}")
        print(f"\nOutfit: {session['outfit_suggestion']}")
        print(f"\nFit card: {session['fit_card']}")

        print("\n\n=== No-results path ===\n")
    session2 = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )
    print(f"Error message: {session2['error']}")
    print(f"Fit card: {session2['fit_card']}")
