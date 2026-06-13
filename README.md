# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.

# FitFindr

FitFindr is a small agent that helps a user find a secondhand clothing item, style it with their wardrobe, and create a short shareable fit-card caption. The project uses a planning loop that connects three tools: listing search, outfit suggestion, and fit-card generation.

---

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root with:

```bash
GROQ_API_KEY=your_groq_api_key_here
```

Run the Gradio app:

```bash
python app.py
```

Open the local URL shown in the terminal.

Run tests:

```bash
pytest tests/
```

---

## Tool Inventory

### Tool 1: `search_listings(description, size=None, max_price=None)`

**Purpose:**
Searches the mock secondhand listing dataset and returns listings that match the user’s requested item.

**Inputs:**

| Parameter     | Type            | Meaning                                             |
| ------------- | --------------- | --------------------------------------------------- |
| `description` | `str`           | Main search phrase, such as `"vintage graphic tee"` |
| `size`        | `str \| None`   | Optional size filter, such as `"M"` or `"XXS"`      |
| `max_price`   | `float \| None` | Optional maximum price filter                       |

**Output:**
Returns a `list[dict]` of matching listings sorted by relevance. Each listing contains:

* `id`
* `title`
* `description`
* `category`
* `style_tags`
* `size`
* `condition`
* `price`
* `colors`
* `brand`
* `platform`

**Failure behavior:**
If no listings match, the tool returns an empty list `[]`. It does not raise an exception.

---

### Tool 2: `suggest_outfit(new_item, wardrobe)`

**Purpose:**
Creates an outfit suggestion using the selected listing and the user’s wardrobe.

**Inputs:**

| Parameter  | Type   | Meaning                                     |
| ---------- | ------ | ------------------------------------------- |
| `new_item` | `dict` | The selected listing from `search_listings` |
| `wardrobe` | `dict` | A wardrobe dictionary with an `items` list  |

**Output:**
Returns a non-empty `str` with 1–2 outfit suggestions. For a normal wardrobe, it names specific wardrobe items and explains how to style them with the new item.

**Failure behavior:**
If the wardrobe is empty, the tool returns general styling advice instead of crashing or returning an empty string.

---

### Tool 3: `create_fit_card(outfit, new_item)`

**Purpose:**
Generates a short social-media-style caption for the outfit.

**Inputs:**

| Parameter  | Type   | Meaning                                        |
| ---------- | ------ | ---------------------------------------------- |
| `outfit`   | `str`  | Outfit suggestion returned by `suggest_outfit` |
| `new_item` | `dict` | Selected listing returned by `search_listings` |

**Output:**
Returns a `str` containing a 2–4 sentence fit-card caption. The caption mentions the item, price, platform, and outfit vibe.

**Failure behavior:**
If the outfit string is empty or missing, the tool returns a descriptive error message string instead of raising an exception.

---

## Planning Loop Explanation

The planning loop is implemented in `run_agent()` inside `agent.py`.

The agent does not blindly call all tools every time. It checks the result of each step before deciding whether to continue.

Flow:

1. Start a new session dictionary using `_new_session()`.
2. Parse the user query into:

   * `description`
   * `size`
   * `max_price`
3. Call `search_listings(description, size, max_price)`.
4. If search results are empty:

   * set `session["error"]`
   * keep `session["selected_item"]` as `None`
   * keep `session["outfit_suggestion"]` as `None`
   * keep `session["fit_card"]` as `None`
   * return early
5. If search results exist:

   * store the full list in `session["search_results"]`
   * store the first result in `session["selected_item"]`
6. Call `suggest_outfit(session["selected_item"], wardrobe)`.
7. Store the returned outfit string in `session["outfit_suggestion"]`.
8. If the outfit suggestion is empty or error-like:

   * set `session["error"]`
   * return early
9. Call `create_fit_card(session["outfit_suggestion"], session["selected_item"])`.
10. Store the returned caption in `session["fit_card"]`.
11. Return the completed session.

This means the agent behaves differently depending on the input. A normal query flows through all three tools, while an impossible search stops immediately after `search_listings`.

---

## State Management

The agent uses a session dictionary as the single source of truth for one interaction.

Session structure:

```python
{
    "query": str,
    "parsed": dict,
    "search_results": list[dict],
    "selected_item": dict | None,
    "wardrobe": dict,
    "outfit_suggestion": str | None,
    "fit_card": str | None,
    "error": str | None,
}
```

State passes between tools like this:

1. `search_listings` returns a list of listings.
2. The planning loop stores the top result as `session["selected_item"]`.
3. `suggest_outfit` receives that exact selected item plus `session["wardrobe"]`.
4. The outfit string is stored as `session["outfit_suggestion"]`.
5. `create_fit_card` receives `session["outfit_suggestion"]` and `session["selected_item"]`.
6. The final caption is stored as `session["fit_card"]`.

This avoids hardcoded values between steps. Each tool receives data produced by the previous step.

---

## Error Handling

| Failure mode       | How it is triggered                                             | Agent behavior                                                                     |
| ------------------ | --------------------------------------------------------------- | ---------------------------------------------------------------------------------- |
| No listings found  | `search_listings("designer ballgown", size="XXS", max_price=5)` | Returns `[]`; the agent sets `session["error"]` and stops before outfit generation |
| Empty wardrobe     | `suggest_outfit(results[0], get_empty_wardrobe())`              | Returns general styling advice instead of crashing                                 |
| Empty outfit input | `create_fit_card("", results[0])`                               | Returns an error message string instead of raising an exception                    |

Concrete tested example:

```bash
python -c "from tools import search_listings; print(search_listings('designer ballgown', size='XXS', max_price=5))"
```

Output:

```text
[]
```

Full agent no-results behavior:

```text
error: I couldn’t find any listings matching that search. Try raising your budget, removing the size filter, or using a broader keyword like 'graphic tee'.
search_results: []
selected_item: None
outfit_suggestion: None
fit_card: None
```

This confirms the agent does not call later tools when search fails.

---

## AI Usage

I used ChatGPT as the AI tool for planning and implementation help.

### Instance 1: Planning document and architecture

**Input given to AI:**
I gave ChatGPT the milestone requirements, the `planning.md` section headers, the required tool descriptions, and the architecture requirements.

**Output produced:**
ChatGPT helped draft specific tool specs, the planning loop logic, state management notes, error handling rows, and a Mermaid architecture diagram.

**What I changed or verified:**
I reviewed the diagram and fixed Mermaid syntax problems by wrapping node labels in quotes. I also made sure the planning loop included the important branch where the agent stops early when `search_listings` returns an empty list.

### Instance 2: Tool implementation and tests

**Input given to AI:**
I gave ChatGPT the `tools.py` stubs, `utils/data_loader.py`, sample listing data, wardrobe schema, and the Tool 1–3 specs from `planning.md`.

**Output produced:**
ChatGPT produced implementations for:

* `search_listings`
* `suggest_outfit`
* `create_fit_card`

It also produced pytest tests for success and failure modes.

**What I changed or verified:**
I checked that `search_listings` used `load_listings()` instead of manually reading JSON. I also verified that no-results search returned `[]`, empty wardrobe returned a useful string, and empty outfit input returned an error message string. I added `tests/conftest.py` to fix the local import path so pytest could import `tools.py`.

### Instance 3: Planning loop and Gradio handler

**Input given to AI:**
I gave ChatGPT `agent.py`, `app.py`, the Planning Loop section, the State Management section, and the architecture diagram.

**Output produced:**
ChatGPT helped implement `run_agent()` and `handle_query()`.

**What I changed or verified:**
I ran `python agent.py` and confirmed the happy path produced a selected item, outfit suggestion, and fit card. I also tested the no-results path and confirmed `session["error"]` was set while `session["fit_card"]` stayed `None`.

---

## Spec Reflection

The most important design decision was making the planning loop branch after `search_listings`. Without this branch, the agent could try to style an item that does not exist. That would make the output confusing and harder to debug.

The session dictionary made the agent easier to reason about because every intermediate result is stored in one place. I could inspect `session["selected_item"]`, `session["outfit_suggestion"]`, and `session["fit_card"]` to verify that state was flowing correctly between tools.

The biggest failure mode was no search results. I handled this by returning early with a specific message that tells the user what to try next, such as raising the budget, removing the size filter, or using a broader keyword.

Another useful design choice was testing tools in isolation before connecting them. This made it easier to tell whether a bug came from one tool or from the planning loop.
