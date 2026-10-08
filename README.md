# FitFindr

> ### 👋 Start here
>
> **New to this repo? Read [RUNNING.md](RUNNING.md) first** — setup, every
> command, and what to do when something breaks.
>
> Once `python test.py` passes:
>
> ```bash
> python app.py listings --full -n 6      # read the data (Milestone 1)
> python app.py fields                    # what you can filter on
> python app.py ask 'vintage graphic tee under $30'
> ```
>
> All three tools are stubs, so that last command will do nothing useful yet.
> That's the starting position.
>
> **The rest of this file is your submission.** Fill it in as you go.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     HOW TO USE THIS FILE

     This is your submission. Fill each section in as you finish the milestone
     it belongs to — don't leave it all to the end.

     Unit 3 asks for the first five sections. Unit 4 adds the five below them.
     Leave the unit 4 sections alone until then; they're here so you know
     what's coming.

     Everything is pasted as TEXT. No screenshots, no images, no video links.
     A typed block of output gets full credit; a picture of the same output
     gets none.
     ───────────────────────────────────────────────────────────────────────── -->

<!-- ═══════════════════════ UNIT 3 — THE BUILD ═══════════════════════ -->

## What This Does

FitFindr takes a natural-language thrift-shopping request and searches a local set of listings by description, size, and maximum price. When it finds a match, the agent selects the top result, asks for outfit ideas using the user's wardrobe, and turns that suggestion into a short fit-card caption. When no listings match, it stops and tells the user which search details to change instead of continuing. The planning logic and state are handled in `agent.py::run_agent`.


---

## Tool Inventory

<!-- Four lines per tool. This is worth 2 points and it's the single most
     common place students lose them.

     "Returns a list" earns NOTHING. The description has to say what is IN
     the list.

     The empty case isn't optional either — it's the thing your loop branches
     on, and if you don't decide it here you'll discover it as a crash in
     Milestone 5. -->

### `search_listings`

- **What it does:** Searches the thrift listings for items matching the requested description, size, and maximum price, then ranks matching items by keyword overlap.
- **Inputs:** `description` (str), `size` (str or None), `max_price` (float or None)
- **Returns:** A list of matching listing dictionaries, each containing the listing's id, title, description, category, style_tags, size, condition, price, colors, brand, and platform, ordered by match score.
- **When it has nothing:** Returns an empty list (`[]`) when no listing matches the filters and description keywords.

### `suggest_outfit`

- **What it does:** Uses the new listing and the user's wardrobe to suggest one or two outfits.
- **Inputs:** `new_item` (dict), `wardrobe` (dict containing an `items` list)
- **Returns:** A non-empty string containing outfit suggestions based on the new item and wardrobe.
- **When it has nothing:** If the wardrobe has no items, returns general styling advice for the new item instead of raising an error or returning an empty string.

### `create_fit_card`

- **What it does:** Uses the selected item and outfit suggestion to create a short social-media-style caption for the find.
- **Inputs:** `outfit` (str), `new_item` (dict)
- **Returns:** A two-to-four sentence caption that mentions the item, price, platform, and overall style or vibe.
- **When it has nothing:** If the outfit is empty or only whitespace, returns a descriptive message instead of raising an error.

## Planning Loop

<!-- Your branch rule, stated as a rule — the condition AND both paths — plus
     the file and function that holds it.

     Like this:
       "If search_listings returns an empty list, put a message in the session
        and stop. Otherwise take the first result and go to suggest_outfit."
        — agent.py::run_agent

     The grader checks your code against what you claim here, so the file and
     function have to be real. -->

**Branch rule:** If `search_listings` returns an empty list, the agent puts a message in `session["error"]` explaining that the user can change the item description, size, or maximum price, then stops. If results are returned, the agent selects the first result and continues to `suggest_outfit`, then `create_fit_card`.

**Where it lives:** `agent.py::run_agent`

**How the query is parsed:** Regular expressions are used to extract an optional size and maximum price from the user's query. The remaining text is used as the description.

**What moves through the session:** The query is stored first, then the parsed description/size/max_price, search results, selected item, wardrobe, outfit suggestion, and finally the fit card. On an empty search, `error` is set and `fit_card` remains `None`.
---

## Sample Run
=== A query the data can match ===
  found: Y2K Baby Tee — Butterfly Print — $18.0 on depop
  outfit: [model-generated outfit suggestion]
  fit card: [model-generated fit-card caption]

=== A query it can't ===
  stopped: No listings matched that search. Try changing the item description, size, or maximum price.
  fit_card is None — it should still be None here
The second one should stop before the fit card...
\

**One full query**

```
$ python app.py ask '...'

```

**The three tools, tested one at a time**

```
$ python -c "from tools import search_listings; print(search_listings('graphic tee', max_price=30))"

```

```
python -c "from tools import suggest_outfit; from utils.data_loader import get_example_wardrobe, load_listings; print(suggest_outfit(load_listings()[0], get_example_wardrobe()))"
```

```
python -c "from tools import create_fit_card; from utils.data_loader import load_listings; print(create_fit_card('jeans and white sneakers', load_listings()[0]))"
```

---

## How I Used AI

### Moment 1 — Implementing the Tools

I asked ChatGPT for help turning the starter tool specifications into working implementations for `search_listings`, `suggest_outfit`, and `create_fit_card`. The response suggested code for each tool, including the required inputs, filtering behavior, wardrobe handling, and model-generated fit cards. I then ran each tool individually from the terminal and kept the implementation after confirming that the outputs matched the intended behavior.

### Moment 2 — Building the Planning Loop

I asked ChatGPT for help implementing `agent.py::run_agent` with session state and a branch for an empty search. The response suggested storing each tool result in the session and stopping when `search_listings` returned an empty list. I tested the agent with both a matching query and a query with no matches, and confirmed that the successful path produced a fit card while the empty path stopped with `session["fit_card"]` still set to `None`.

<!-- ═══════════════════════ UNIT 4 — THE TEST ═══════════════════════

     Don't fill these in during unit 3.
     ═══════════════════════════════════════════════════════════════════ -->

---

## Run Log — Before

<!-- Five criteria, five tries each, in this exact format.

     Five, because your criteria are written out of five. Mark each try PASS
     or FAIL, count the passes, and read that count against your target — a
     row targeting 4 of 5 with three PASS cells is MISSED (3/5).

     `python run_eval.py --label before` runs everything and writes the table
     into results/. Paste it here and fill in the verdicts. -->

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Real output from one try**, pasted as text, naming the file and function
that produced it:

```

```

---

## Verdicts and Diagnoses

<!-- MET or MISSED per criterion against LAST UNIT's target, plus a sentence on
     how you decided.

     Then, for every miss: which of the four places it happened — a tool, the
     loop's branch, the session, or the model's output — AND the mechanism.

     Not a diagnosis:  "The fit card was bad."
     A diagnosis:      "The fit card criterion missed on 2 of 5 items. Both had
                        an empty brand field. My prompt puts the brand in the
                        first sentence, so the card opened with a blank and read
                        like a fragment. The tool worked; the prompt assumed a
                        field that isn't always there."

     Look for a pattern. Three misses on the same tool is one problem, not
     three. -->

| # | Criterion | Target | Verdict | How I decided |
|---|---|---|---|---|
| 1 |  |  |  |  |
| 2 |  |  |  |  |
| 3 |  |  |  |  |
| 4 |  |  |  |  |
| 5 |  |  |  |  |

**Diagnoses**



---

## Loop Trace

<!-- One full run, printed step by step, with the MCP call visible in it.

     `python app.py ask '...' --trace` once you've added the trace.step()
     calls in Milestone 2.

     Worth pasting BOTH the happy path and the empty-search path. The empty
     one should be visibly shorter, because it stops. If your two traces are
     the same length, your branch isn't working — and this is the fastest way
     anyone will ever find that out. -->

**Happy path**

```
[1] parse_query
      in:  vintage graphic hoodie under $30
      out: dict with keys: description, size, max_price
[2] search_listings (via MCP)
      in:  dict with keys: description, size, max_price
      out: 10 items: Vintage Graphic Hoodie — Faded Black, Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style … +7 more
[3] select_item
      in:  10 items: Vintage Graphic Hoodie — Faded Black, Y2K Baby Tee — Butterfly Print, Graphic Tee — 2003 Tour Bootleg Style … +7 more
      out: Vintage Graphic Hoodie — Faded Black ($26.0, depop)
[4] suggest_outfit
      in:  dict with keys: new_item, wardrobe
      out: Hey there! That vintage graphic hoodie is an absolute goldmine—the faded black wash and subtle pilling give it…
[5] create_fit_card
      in:  dict with keys: outfit, new_item
      out: Scored this faded black vintage graphic hoodie on Depop for just $26, and the perfectly worn-in pilling gives …

```

**Empty search**

```

```

**On the MCP move:** <!-- what changed in your code, and whether anything
behaved differently afterwards. If the rewire didn't work, say exactly where it
broke — the error text and the last thing that worked. That earns the point in
full. -->
I moved `search_listings` from a direct Python function call to the MCP server. The agent now calls it through `mcp_client.call_tool()`. The returned search results behaved the same as before, and the normal FitFindr flow continued to work.


---

## The Improvement

<!-- What you changed, why your diagnosis pointed at it, and the after-run in
     the same table format. One change, measured properly.

     `python run_eval.py --label after` -->

**What I changed:**

**Which failure it was meant to fix:**

### Run Log — After

| Criterion | Target | Try 1 | Try 2 | Try 3 | Try 4 | Try 5 | Verdict |
|---|---|---|---|---|---|---|---|
| 1.  |  |  |  |  |  |  |  |
| 2.  |  |  |  |  |  |  |  |
| 3.  |  |  |  |  |  |  |  |
| 4.  |  |  |  |  |  |  |  |
| 5.  |  |  |  |  |  |  |  |

**Did it help, and how do I know:**

<!-- If it made things worse, say that. Honestly reported, that earns full
     credit and is more interesting than one that worked. -->



---

## What's Still Broken

<!-- For each criterion still missed: what you'd do, and why you stopped where
     you did. "I ran out of time" is fine if it's true. Pretending nothing is
     left is not. -->



<!-- ═════════════════════════════════════════════════════════════════════

     SUBMISSION CHECKLIST — unit 3

       [ ] criteria.md has five numbered criteria, each with a target
       [ ] Each criterion has a reason underneath it
       [ ] All five unit 3 sections above have real content
       [ ] Tool Inventory: all three tools, inputs WITH TYPES, a specific
           return value, and the empty case
       [ ] Planning Loop names the branch rule and agent.py::run_agent
       [ ] Sample Run: one full query plus the three per-tool tests, as text
       [ ] At least four new commits
       [ ] Repository URL submitted — WRITE IT DOWN, you submit the same one
           next unit

     SUBMISSION CHECKLIST — unit 4

       [ ] mcp_server.py exists with one tool registered
           (or a written record of exactly where the rewire broke)
       [ ] Run Log — Before, five criteria, five tries each
       [ ] Real output pasted underneath, naming file and function
       [ ] A verdict on every criterion
       [ ] A diagnosis for every miss, naming a place AND a mechanism
       [ ] Loop Trace, with the MCP call visible in it
       [ ] All three failure modes triggered and handled
       [ ] One improvement, with Run Log — After in the same format
       [ ] What's Still Broken
       [ ] At least four new commits
       [ ] The SAME repository URL as last unit

     Do not delete and recreate this repository. Your commit history is what
     shows your criteria existed before your results did.
     ═════════════════════════════════════════════════════════════════════ -->

---

📖 **How to run this project: [RUNNING.md](RUNNING.md)**
