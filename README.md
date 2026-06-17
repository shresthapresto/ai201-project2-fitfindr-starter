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
---

## Tool Inventory

**search_listings(description: str, size: str | None, max_price: float | None) → list[dict]**
Searches 40 mock secondhand listings by keyword relevance. Filters by size and
price ceiling if provided, then scores remaining listings by how many description
keywords appear in the title, description, and style tags. Returns a list of
matching listing dicts sorted best-first, or an empty list if nothing matches.

**suggest_outfit(new_item: dict, wardrobe: dict) → str**
Uses the Groq LLM to suggest 1-2 complete outfits. If the wardrobe has items,
it builds a prompt with the wardrobe contents and asks for specific pairings.
If the wardrobe is empty, it asks for general styling advice instead. Always
returns a non-empty string.

**create_fit_card(outfit: str, new_item: dict) → str**
Uses the Groq LLM to generate a 2-4 sentence casual Instagram/TikTok caption
for the thrifted find. Mentions the item name, price, and platform naturally.
Uses temperature=0.9 so outputs vary across runs. Returns an error string if
outfit input is empty.

---

## Planning Loop

The agent runs a fixed sequence with one conditional branch. It does not
re-plan or loop — each step feeds into the next.

1. Parse the query using regex to extract a description, size, and max_price
2. Call search_listings with the parsed parameters
3. If results is empty, set an error message and return early — suggest_outfit
   is never called with empty input
4. If results exist, pick results[0] as the selected item
5. Call suggest_outfit with the selected item and the user's wardrobe
6. Call create_fit_card with the outfit suggestion and selected item
7. Return the completed session dict

The only decision point is after search_listings: empty results trigger an
early exit, non-empty results continue the chain.

---

## State Management

All state lives in a session dict initialized at the start of each run:

- `session["parsed"]` — extracted description, size, max_price from the query
- `session["search_results"]` — full list returned by search_listings
- `session["selected_item"]` — results[0], passed into suggest_outfit
- `session["outfit_suggestion"]` — string returned by suggest_outfit, passed into create_fit_card
- `session["fit_card"]` — final caption string
- `session["error"]` — set on early exit, None on success

Each tool reads its inputs from the session and writes its output back. No tool
re-fetches or recomputes data from a previous step.

---

## Error Handling

| Tool | Failure mode | What happens |
|------|-------------|--------------|
| search_listings | No listings match | session["error"] is set to "No listings matched your search — try broader keywords, remove the size filter, or raise your price ceiling." Agent returns immediately without calling the next tool. |
| suggest_outfit | Wardrobe is empty | Tool detects empty wardrobe["items"] and switches to a general styling advice prompt. Returns useful string instead of crashing. |
| create_fit_card | outfit string is empty | Returns "Could not generate a fit card — outfit suggestion was missing." instead of raising an exception. |

**Concrete example from testing:**
Running `search_listings("designer ballgown", size="XXS", max_price=5)` returned
`[]`. The agent set session["error"] = "No listings matched..." and returned
without calling suggest_outfit or create_fit_card. The UI showed the error in
the first panel with the other two blank.

---

## Spec Reflection

The planning loop matched the spec closely — the fixed sequence with one
conditional branch worked well for this problem since the tools always run
in the same order. The wardrobe schema used `name` and `colors` (a list)
instead of `title` and `color` (a string), which required a fix after checking
the actual data. If extending this, I'd add a query clarification step so the
agent could ask for size or price range if neither was provided.

---

## AI Usage

**Instance 1 — search_listings implementation**
I gave Claude the Tool 1 spec block from planning.md (inputs, return value,
failure mode) and asked it to implement the function using load_listings().
The generated code filtered by price and size correctly. Before running it
I verified it handled the empty-results case by returning [] instead of raising
an exception. Tested with 3 queries: a matching query, an impossible price, and
a size filter.

**Instance 2 — suggest_outfit implementation**
I gave Claude the Tool 2 spec and asked it to implement using Groq's
llama-3.3-70b-versatile. The generated code used `i['title']` and `i['color']`
for wardrobe items, which caused a KeyError at runtime. I fixed it to
`i['name']` and `', '.join(i['colors'])` after printing the actual wardrobe
item structure to check the field names.

**Instance 3 — run_agent planning loop**
I gave Claude the Planning Loop and State Management sections from planning.md
plus the Architecture diagram and asked it to implement run_agent() in agent.py.
The generated code included dead stub code after the return statement. I removed
those lines before running. Verified the empty-results branch returned early
before calling suggest_outfit.