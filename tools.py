"""
tools.py

The three required FitFindr tools. Each tool is a standalone function that
can be called and tested independently before being wired into the agent loop.

Complete and test each tool before moving to agent.py.

Tools:
    search_listings(description, size, max_price)  → list[dict]
    suggest_outfit(new_item, wardrobe)              → str
    create_fit_card(outfit, new_item)               → str
"""

import os
import re
from typing import Any

from dotenv import load_dotenv
from groq import Groq

from utils.data_loader import load_listings

load_dotenv()


# ── Groq client ───────────────────────────────────────────────────────────────

def _get_groq_client():
    """Initialize and return a Groq client using GROQ_API_KEY from .env."""
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to a .env file in the project root."
        )
    return Groq(api_key=api_key)

GROQ_MODEL = "llama-3.3-70b-versatile"


def _tokenize(text: str) -> set[str]:
    """Return lowercase searchable tokens from text."""
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def _stringify_list(values: Any) -> str:
    """Safely convert a list-like field into searchable text."""
    if not values:
        return ""
    if isinstance(values, list):
        return " ".join(str(value) for value in values if value is not None)
    return str(values)


def _format_listing_for_prompt(item: dict) -> str:
    """Format a listing or wardrobe item compactly for an LLM prompt."""
    name = item.get("title") or item.get("name") or "Unnamed item"
    category = item.get("category", "unknown category")
    colors = _stringify_list(item.get("colors")) or "unknown colors"
    tags = _stringify_list(item.get("style_tags")) or "no style tags"
    notes = item.get("notes")
    price = item.get("price")
    platform = item.get("platform")
    condition = item.get("condition")

    details = [f"{name} ({category})", f"colors: {colors}", f"tags: {tags}"]

    if price is not None:
        details.append(f"price: ${price}")
    if platform:
        details.append(f"platform: {platform}")
    if condition:
        details.append(f"condition: {condition}")
    if notes:
        details.append(f"notes: {notes}")

    return " | ".join(details)


def _call_groq(messages: list[dict[str, str]], temperature: float = 0.7) -> str:
    """Call Groq and return message content. Return an error string on failure."""
    try:
        client = _get_groq_client()
        completion = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=messages,
            temperature=temperature,
            max_tokens=350,
        )
        content = completion.choices[0].message.content
        return content.strip() if content else "Error: the LLM returned an empty response."
    except Exception as exc:
        return f"Error: could not generate an LLM response. {exc}"

# ── Tool 1: search_listings ───────────────────────────────────────────────────

def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search the mock listings dataset for items matching the description,
    optional size, and optional price ceiling.
    """
    query = (description or "").strip().lower()
    if not query:
        return []

    query_tokens = _tokenize(query)
    if not query_tokens:
        return []

    listings = load_listings()
    scored_results: list[tuple[int, dict]] = []

    for listing in listings:
        if max_price is not None and float(listing.get("price", 0)) > max_price:
            continue

        if size is not None:
            requested_size = size.strip().lower()
            listing_size = str(listing.get("size", "")).lower()
            if requested_size not in listing_size and listing_size not in requested_size:
                continue

        title = str(listing.get("title", "")).lower()
        listing_description = str(listing.get("description", "")).lower()
        category = str(listing.get("category", "")).lower()
        style_tags = _stringify_list(listing.get("style_tags")).lower()
        colors = _stringify_list(listing.get("colors")).lower()
        brand = str(listing.get("brand") or "").lower()

        searchable_text = " ".join(
            [title, listing_description, category, style_tags, colors, brand]
        )
        searchable_tokens = _tokenize(searchable_text)

        score = 0

        token_matches = query_tokens & searchable_tokens
        score += len(token_matches)

        if query in title:
            score += 5
        if query in listing_description:
            score += 3
        if query in style_tags:
            score += 4
        if query in category:
            score += 2
        if query in colors:
            score += 2
        if brand and query in brand:
            score += 2

        if score > 0:
            scored_results.append((score, listing))

    scored_results.sort(
        key=lambda scored: (-scored[0], float(scored[1].get("price", 0)))
    )

    return [listing for _, listing in scored_results]
# ── Tool 2: suggest_outfit ────────────────────────────────────────────────────

def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Given a thrifted item and the user's wardrobe, suggest 1–2 complete outfits.
    """
    if not isinstance(new_item, dict) or not new_item:
        return "I couldn't suggest an outfit because the selected item is missing."

    wardrobe_items = []
    if isinstance(wardrobe, dict):
        wardrobe_items = wardrobe.get("items") or []

    if not wardrobe_items:
        item_name = new_item.get("title", "this item")
        item_tags = _stringify_list(new_item.get("style_tags"))
        item_colors = _stringify_list(new_item.get("colors"))

        return (
            f"I found {item_name}, but your wardrobe is empty, so I can't build a "
            "personalized outfit from your own pieces yet. General styling idea: "
            f"use the item's {item_colors or 'main'} colors and "
            f"{item_tags or 'style'} vibe as the base, then pair it with simple "
            "wardrobe basics like jeans, neutral shoes, and one outerwear layer."
        )

    formatted_new_item = _format_listing_for_prompt(new_item)
    formatted_wardrobe = "\n".join(
        f"- {_format_listing_for_prompt(item)}" for item in wardrobe_items
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are FitFindr, a practical outfit styling assistant. "
                "Give concise, specific styling advice using the user's actual wardrobe items. "
                "Do not invent wardrobe items."
            ),
        },
        {
            "role": "user",
            "content": (
                "Suggest 1–2 complete outfits using this new thrifted item and the wardrobe below.\n\n"
                f"New item:\n{formatted_new_item}\n\n"
                f"Wardrobe:\n{formatted_wardrobe}\n\n"
                "Requirements:\n"
                "- Mention the exact wardrobe item names you use.\n"
                "- Explain the overall vibe.\n"
                "- Include 1–2 concrete styling notes like layering, cuffing, tucking, or accessories.\n"
                "- Keep the response under 160 words."
            ),
        },
    ]

    return _call_groq(messages, temperature=0.7)
# ── Tool 3: create_fit_card ───────────────────────────────────────────────────

def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Generate a short, shareable outfit caption for the thrifted find.
    """
    if not outfit or not outfit.strip():
        return (
            "Error: I couldn't create a fit card because the outfit suggestion "
            "is empty or missing."
        )

    if not isinstance(new_item, dict) or not new_item:
        return (
            "Error: I couldn't create a fit card because the selected item "
            "is missing."
        )

    item_title = new_item.get("title", "this thrifted item")
    price = new_item.get("price")
    platform = new_item.get("platform", "the resale platform")
    condition = new_item.get("condition", "unknown condition")

    price_text = f"${price:g}" if isinstance(price, int | float) else "an unknown price"

    messages = [
        {
            "role": "system",
            "content": (
                "You write casual outfit captions for thrifted fashion finds. "
                "Sound natural, specific, and social-media ready. Avoid sounding like an ad."
            ),
        },
        {
            "role": "user",
            "content": (
                "Create a 2–4 sentence Instagram/TikTok-style fit card caption.\n\n"
                f"New item: {item_title}\n"
                f"Price: {price_text}\n"
                f"Platform: {platform}\n"
                f"Condition: {condition}\n"
                f"Outfit suggestion: {outfit}\n\n"
                "Requirements:\n"
                "- Mention the item name, price, and platform naturally once each.\n"
                "- Capture the outfit vibe in specific terms.\n"
                "- Sound casual and authentic.\n"
                "- Do not use hashtags.\n"
            ),
        },
    ]

    return _call_groq(messages, temperature=0.95)