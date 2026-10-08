"""
The FitFindr planning loop.

The loop uses session state to carry information from one tool call
to the next and branches when a search returns no results.
"""

import re

import trace
from tools import suggest_outfit, create_fit_card
from mcp_client import call_tool
from generate import ModelUnavailable

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
    trace.start_trace()

    count = 0
    count += 1
    trace.check_iterations(count)

    # Parse the user's query.
    session["parsed"] = _parse_query(query)

    trace.step(
        "parse_query",
        inputs=query,
        returned=session["parsed"],
    )

    # Search through MCP.
    search_inputs = {
        "description": session["parsed"]["description"],
        "size": session["parsed"]["size"],
        "max_price": session["parsed"]["max_price"],
    }

    session["search_results"] = call_tool(
        "search_listings",
        search_inputs,
    )

    trace.step(
        "search_listings (via MCP)",
        inputs=search_inputs,
        returned=session["search_results"],
    )

    # Branch: stop if the search is empty.
    if not session["search_results"]:
        session["error"] = (
            "No listings matched that search. Try changing the item description, "
            "size, or maximum price."
        )

        trace.step(
            "empty-search branch",
            returned=session["error"],
            note="branch: empty, stopping",
        )

        return session

    # Select the first result.
    session["selected_item"] = session["search_results"][0]

    trace.step(
        "select_item",
        inputs=session["search_results"],
        returned=session["selected_item"],
    )

    # Generate outfit advice.
    outfit_inputs = {
        "new_item": session["selected_item"],
        "wardrobe": session["wardrobe"],
    }

    try:
        session["outfit_suggestion"] = suggest_outfit(
            session["selected_item"],
            session["wardrobe"],
        )
    except ModelUnavailable:
        session["error"] = (
            "The styling model could not be reached. "
            "Check your API key or try again later."
        )

        trace.step(
            "suggest_outfit",
            inputs=outfit_inputs,
            returned="ModelUnavailable",
            note="stopping",
        )

        return session

    trace.step(
        "suggest_outfit",
        inputs=outfit_inputs,
        returned=session["outfit_suggestion"],
    )

    # Generate the fit card.
    fit_card_inputs = {
        "outfit": session["outfit_suggestion"],
        "new_item": session["selected_item"],
    }

    try:
        session["fit_card"] = create_fit_card(
            session["outfit_suggestion"],
            session["selected_item"],
        )
    except ModelUnavailable:
        session["error"] = (
            "The styling model could not be reached. "
            "Check your API key or try again later."
        )

        trace.step(
            "create_fit_card",
            inputs=fit_card_inputs,
            returned="ModelUnavailable",
            note="stopping",
        )

        return session

    trace.step(
        "create_fit_card",
        inputs=fit_card_inputs,
        returned=session["fit_card"],
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