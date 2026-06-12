# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): ...
- `size` (str): ...
- `max_price` (float): ...

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->

---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): ...
- `wardrobe` (dict): ...

**What it returns:**
<!-- Describe the return value -->

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (...): ...

**What it returns:**
<!-- Describe the return value -->

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | |
| suggest_outfit | Wardrobe is empty | |
| create_fit_card | Outfit input is missing or incomplete | |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->

**Milestone 3 — Individual tool implementations:**

**Milestone 4 — Planning loop and state management:**

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
The agent calls search_listings("vintage graphic tee", max_price=30.0). This searches the listings data for items that match the user’s request, using fields like title, description, category, style tags, size, condition, price, colors, brand, and platform.

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->
search_listings returns matching listings sorted by relevance. For example, it might return a top result like "Faded Band Tee", priced at $22, from Depop, in Good condition. The agent selects the best matching listing as the new item.

**Step 3:**
<!-- Continue until the full interaction is complete -->
The agent calls suggest_outfit(new_item=<Faded Band Tee>, wardrobe=<user wardrobe>). This tool uses the selected listing plus the user’s wardrobe items and style context, such as baggy jeans and chunky sneakers, to create a complete outfit suggestion.

**Step 4:**
suggest_outfit returns a styling recommendation, such as pairing the tee with wide-leg jeans and chunky sneakers for a 90s grunge look. The agent then calls create_fit_card(outfit=<outfit suggestion>, new_item=<Faded Band Tee>) to turn the outfit into a short shareable caption.

**Final output to user:**
<!-- What does the user actually see at the end? -->
The user sees the recommended item, why it matches their request, how to style it with their wardrobe, and a fit card caption. For example: “I found a Faded Band Tee on Depop for $22 in good condition. Pair it with your baggy jeans and chunky sneakers for a relaxed 90s grunge look. Fit card: ‘thrifted this faded band tee off depop for $22 and honestly it was made for my wide-legs 🖤 full look in my stories.’”

**Error path:**
If search_listings returns no results, the agent stops instead of calling suggest_outfit or create_fit_card. It tells the user no matching listings were found and suggests changing the search, such as raising the budget, removing a size filter, or trying a broader keyword like “graphic tee.”
