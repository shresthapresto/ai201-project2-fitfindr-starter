# FitFindr — planning.md

> Complete this document before writing any implementation code.
> Your spec and agent diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Your planning.md will be reviewed as part of your submission.
> Update it before starting any stretch features.

**Example user query:**
FitFindr takes a natural language query, searches a secondhand listings dataset 
for matching items, and uses an LLM to suggest outfits and generate a shareable 
caption. Each tool is triggered in sequence — search first, then outfit suggestion 
using the top result, then the fit card using the outfit. If search returns nothing, 
the agent stops and tells the user to try a broader query instead of passing empty 
input to the next tool.

---

## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Searches the mock listings dataset for items matching a text description, 
optional size, and optional price ceiling. Returns a ranked list of matches 
sorted by keyword relevance.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): Keywords describing the item the user wants (e.g. "vintage graphic tee")
- `size` (str | None): Size to filter by (e.g. "M"), or None to skip size filtering
- `max_price` (float | None): Maximum price inclusive (e.g. 30.0), or None to skip price filtering

**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
A list of listing dicts sorted by relevance score, each containing: id, title, 
description, category, style_tags (list), size, condition, price (float), 
colors (list), brand, platform. Returns an empty list if nothing matches.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
The agent sets session["error"] to "No listings matched — try broader keywords, 
remove the size filter, or raise your price ceiling." and returns the session 
immediately without calling the next tool.
---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Uses an LLM to suggest 1-2 complete outfits pairing the new thrifted item with 
pieces from the user's wardrobe, or gives general styling advice if the wardrobe is empty.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): The listing dict for the item the user is considering buying
- `wardrobe` (dict): A dict with an 'items' key containing a list of wardrobe item 
  dicts (may be empty)

**What it returns:**
<!-- Describe the return value -->
A non-empty string with outfit suggestions — either specific pairings using named 
wardrobe pieces, or general styling advice if the wardrobe is empty.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
If wardrobe['items'] is empty, skip wardrobe-specific suggestions and ask the LLM 
for general styling ideas instead. Never return an empty string.
---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
Uses an LLM to generate a 2-4 sentence casual Instagram/TikTok caption for the 
thrifted outfit, mentioning the item name, price, and platform naturally.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (str): The outfit suggestion string from suggest_outfit()
- `new_item` (dict): The listing dict containing title, price, and platform

**What it returns:**
<!-- Describe the return value -->
A 2-4 sentence string written like a real OOTD post caption. If outfit is empty, 
returns a descriptive error message string instead.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
If outfit is empty or whitespace, return the string "Could not generate a fit card 
— outfit suggestion was missing." Do not raise an exception.

---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->
The agent runs a fixed sequence with one conditional branch. First it parses the 
query to extract description, size, and max_price. Then it calls search_listings — 
if results is empty, it sets an error in the session and returns early. If results 
exist, it sets selected_item = results[0] and calls suggest_outfit. Then it calls 
create_fit_card with the outfit suggestion and selected item. The agent knows it's 
done when fit_card is set in the session or an error caused early return.
---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->
All state is stored in a session dict initialized at the start of each run. 
search_listings results are stored in session["search_results"], the top result 
in session["selected_item"], the LLM output in session["outfit_suggestion"], 
the caption in session["fit_card"], and any early-exit message in session["error"]. 
Each tool reads its inputs from the session and writes its output back to the session.
---

## Error Handling

| search_listings | No results match the query | Set session["error"] = "No listings matched — try broader keywords, remove size filter, or raise price ceiling." Return session immediately. |
| suggest_outfit | Wardrobe is empty | Call LLM for general styling advice instead of wardrobe pairings. Return that string — never crash or return empty. |
| create_fit_card | Outfit input is missing or incomplete | Return the string "Could not generate a fit card — outfit suggestion was missing." instead of raising an exception. |
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
User query
    │
    ▼
Planning Loop
    │
    ├─► parse query → description, size, max_price
    │       │
    │       ▼
    ├─► search_listings(description, size, max_price)
    │       │ results=[]
    │       ├──► session["error"] = "No listings matched..." → return session
    │       │
    │       │ results=[item, ...]
    │       ▼
    │   session["selected_item"] = results[0]
    │       │
    ├─► suggest_outfit(selected_item, wardrobe)
    │       │ wardrobe empty → LLM gives general advice
    │       │ wardrobe has items → LLM gives specific pairings
    │       ▼
    │   session["outfit_suggestion"] = "..."
    │       │
    └─► create_fit_card(outfit_suggestion, selected_item)
            │ outfit empty → return error string
            │ outfit present → LLM generates caption
            ▼
        session["fit_card"] = "..."
            │
            ▼
        Return session
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
For search_listings, I'll give Claude the Tool 1 spec block (inputs, return value, 
failure mode) and ask it to implement the function using load_listings(). I'll verify 
the output filters by all three parameters and handles empty results, then test with 
3 queries: one that returns results, one with an impossible price, one with a size filter.

For suggest_outfit, I'll give Claude the Tool 2 spec and ask it to implement using 
Groq's llama-3.3-70b-versatile. I'll verify it handles the empty wardrobe branch 
before running it, then test with both get_example_wardrobe() and get_empty_wardrobe().

For create_fit_card, I'll give Claude the Tool 3 spec and ask it to implement with 
temperature=0.9. I'll verify the empty-outfit guard is present, then run it 3 times 
on the same input to confirm outputs vary.

**Milestone 4 — Planning loop and state management:**
I'll give Claude the Planning Loop, State Management sections, and the Architecture 
diagram and ask it to implement run_agent() in agent.py. I'll verify the generated 
code branches on empty search results and doesn't call all three tools unconditionally. 
Then I'll run both test cases already in agent.py (happy path and no-results path).

---

## A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
The agent parses the query and extracts description = "vintage graphic tee", 
max_price = 30.0, size = None. It calls search_listings("vintage graphic tee", 
size=None, max_price=30.0), which filters and scores all 40 listings and returns 
matches sorted by relevance. The agent stores results[0] — e.g. "Faded Band Tee, 
$22, Depop" — in session["selected_item"].

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->
The agent calls suggest_outfit(new_item=session["selected_item"], wardrobe=example_wardrobe). 
The tool formats the wardrobe into a prompt and asks the LLM for 1-2 outfit combinations 
using the band tee and specific wardrobe pieces. The result is stored in 
session["outfit_suggestion"].

**Step 3:**
<!-- Continue until the full interaction is complete -->
The agent calls create_fit_card(outfit=session["outfit_suggestion"], 
new_item=session["selected_item"]). The LLM writes a casual 2-4 sentence OOTD caption 
mentioning the item, price, and platform. The result is stored in session["fit_card"].

**Final output to user:**
<!-- What does the user actually see at the end? -->
The Gradio UI shows three panels: listing details (title, price, size, condition, 
platform), the outfit suggestion paragraph, and the fit card caption ready to copy.