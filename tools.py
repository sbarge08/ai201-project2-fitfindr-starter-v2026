"""
The three FitFindr tools.

Each tool is standalone so it can be tested independently before being
connected to the planning loop.
"""

import re

import config
from generate import generate
from utils.data_loader import load_listings


def _size_matches(requested_size: str, listing_size: str) -> bool:
    """Return True when the requested size matches the listing size."""
    requested = requested_size.strip().lower()
    actual = listing_size.strip().lower()

    if requested == actual:
        return True

    # Handle sizes such as "S/M" without treating "L" as a match for "XL".
    parts = [part.strip() for part in actual.split("/")]

    if requested in parts:
        return True

    # Handle common numeric shoe/waist sizes such as "8" or "W28".
    if requested == actual.replace(" ", ""):
        return True

    return False


def search_listings(
    description: str,
    size: str | None = None,
    max_price: float | None = None,
) -> list[dict]:
    """
    Search listings by description keywords, optional size, and price ceiling.

    Returns matching listing dictionaries ordered by keyword-match score.
    Returns [] when nothing matches.
    """
    listings = load_listings()

    # Turn the search description into useful lowercase keywords.
    keywords = set(re.findall(r"[a-z0-9]+", description.lower()))

    scored = []

    for listing in listings:
        if max_price is not None and listing["price"] > max_price:
            continue

        if size is not None and not _size_matches(size, listing["size"]):
            continue

        searchable_text = " ".join(
            [
                listing["title"],
                listing["description"],
                listing["category"],
                " ".join(listing["style_tags"]),
            ]
        ).lower()

        score = sum(
            1
            for keyword in keywords
            if keyword in searchable_text
        )

        if score > 0:
            scored.append((score, listing))

    scored.sort(key=lambda item: item[0], reverse=True)

    return [
        listing
        for _, listing in scored[: config.SEARCH_RESULT_LIMIT]
    ]


def suggest_outfit(new_item: dict, wardrobe: dict) -> str:
    """
    Suggest one or two outfits using the new item and user's wardrobe.

    If the wardrobe is empty, return general styling advice.
    """
    items = wardrobe.get("items", [])

    item_details = (
        f"Title: {new_item.get('title', 'Unknown item')}\n"
        f"Description: {new_item.get('description', '')}\n"
        f"Category: {new_item.get('category', '')}\n"
        f"Style tags: {', '.join(new_item.get('style_tags', []))}\n"
        f"Colors: {', '.join(new_item.get('colors', []))}\n"
        f"Size: {new_item.get('size', '')}\n"
    )

    if not items:
        prompt = f"""
You are a fashion stylist.

Suggest one or two general outfit ideas for this thrifted item.
The user has not provided any wardrobe items, so do not invent specific
pieces that the user owns.

NEW ITEM:
{item_details}

Give practical styling advice that matches the item's style, colors, and
category.
""".strip()
    else:
        wardrobe_text = "\n".join(
            f"- {item.get('name', item.get('title', 'Unknown piece'))}: "
            f"{item}"
            for item in items
        )

        prompt = f"""
You are a fashion stylist.

Suggest one or two outfits using the new thrifted item and pieces from
the user's existing wardrobe. Name the wardrobe pieces you use.

NEW ITEM:
{item_details}

USER'S WARDROBE:
{wardrobe_text}

Keep the suggestions practical and explain briefly why the pieces work
together.
""".strip()

    response = generate(prompt)

    return response.strip()


def create_fit_card(outfit: str, new_item: dict) -> str:
    """
    Create a short social-media-style caption for the selected item.

    Returns a descriptive message if outfit is empty.
    """
    if not outfit or not outfit.strip():
        return "No outfit suggestion was provided, so a fit card could not be created."

    prompt = f"""
Write a short social-media-style fit card caption for this thrift find.

The caption must:
- be 2 to 4 sentences
- mention the item
- mention its price
- mention its platform
- describe the overall vibe
- connect the caption to the suggested outfit
- sound like a real fashion post, not a product listing

ITEM:
Title: {new_item.get('title', 'Unknown item')}
Description: {new_item.get('description', '')}
Price: ${new_item.get('price', '')}
Platform: {new_item.get('platform', '')}
Style tags: {', '.join(new_item.get('style_tags', []))}
Colors: {', '.join(new_item.get('colors', []))}

OUTFIT:
{outfit}
""".strip()

    response = generate(prompt)

    return response.strip()