"""
The FitFindr planning loop.

The loop uses session state to carry information from one tool call
to the next and branches when a search returns no results.
"""

import re

import trace
from tools import search_listings, suggest_outfit, create_fit_card


def new_session(query: str, wardrobe: dict) -> dict:
    """
    Create a fresh session for one user interaction.
    """
    return {
        "query": query,
        "parsed": {},
        "search_results": [],
        "selected_item": None,
        "wardrobe": wardrobe,
        "outfit_suggestion": None,
        "fit_card": None,
        "error": None,
    }


def _parse_query(query: str) -> dict:
    """
    Parse description, size, and maximum price from a natural-language query.

    This uses regular expressions for the optional size and price fields.
    """
    max_price = None
    size = None

    price_match = re.search(
        r"(?:under|below|up to|max(?:imum)?(?: price)? of?)\s*\$?(\d+(?:\.\d+)?)",
        query,
        flags=re.IGNORECASE,
    )

    if price_match:
        max_price = float(price_match.group(1))

    size_match = re.search(
        r"\bsize\s+([A-Za-z0-9]+(?:/[A-Za-z0-9]+)?(?:\s*\([^)]*\))?)",
        query,
        flags=re.IGNORECASE,
    )

    if size_match:
        size = size_match.group(1).strip()

    description = query

    if price_match:
        description = description.replace(price_match.group(0), " ")

    if size_match:
        description = description.replace(size_match.group(0), " ")

    description = re.sub(r"\s+", " ", description).strip()

    return {
        "description": description,
        "size": size,
        "max_price": max_price,
    }


def run_agent(query: str, wardrobe: dict) -> dict:
    """
    Run the FitFindr planning loop once and return the finished session.
    """
    session = new_session(query, wardrobe)

    # This Unit 3 loop has a fixed sequence with one important branch:
    # search -> empty? stop : select item -> outfit -> fit card.
    count = 0
    count += 1
    trace.check_iterations(count)

    # Parse the user's query and save the parsed state.
    session["parsed"] = _parse_query(query)

    # Search using the parsed values.
    session["search_results"] = search_listings(
        session["parsed"]["description"],
        size=session["parsed"]["size"],
        max_price=session["parsed"]["max_price"],
    )

    # Branch: an empty search must stop before suggest_outfit.
    if not session["search_results"]:
        session["error"] = (
            "No listings matched that search. Try changing the item description, "
            "size, or maximum price."
        )
        return session

    # Carry the first search result through session state.
    session["selected_item"] = session["search_results"][0]

    # Use the selected item from session state.
    session["outfit_suggestion"] = suggest_outfit(
        session["selected_item"],
        session["wardrobe"],
    )

    # Use both the outfit and selected item from session state.
    session["fit_card"] = create_fit_card(
        session["outfit_suggestion"],
        session["selected_item"],
    )

    return session


def _show(session: dict) -> None:
    if session["error"]:
        print(f"  stopped: {session['error']}")
        print(f"  fit_card is {session['fit_card']!r} — it should still be None here")
        return

    item = session["selected_item"] or {}
    print(
        f"  found:    {item.get('title')} — "
        f"${item.get('price')} on {item.get('platform')}"
    )
    print(f"  outfit:   {session['outfit_suggestion']}")
    print(f"  fit card: {session['fit_card']}")


if __name__ == "__main__":
    from utils.data_loader import get_example_wardrobe

    print("=== A query the data can match ===")
    _show(
        run_agent(
            query="looking for a vintage graphic tee under $30",
            wardrobe=get_example_wardrobe(),
        )
    )

    print("\n=== A query it can't ===")
    _show(
        run_agent(
            query="designer ballgown size XXS under $5",
            wardrobe=get_example_wardrobe(),
        )
    )

    print(
        "\nThe second one should stop before the fit card. "
        "If both paths look the same,\nthe branch isn't doing anything yet."
    )