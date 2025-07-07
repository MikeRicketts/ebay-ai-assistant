def evaluate_listing(listing):
    """
    Evaluate the quality of a generated listing.
    Returns a score from 0-100 and improvement suggestions.
    """
    score = 100
    suggestions = []

    # Check title length and quality
    title = listing.get("title", "")
    if not title:
        score -= 30
        suggestions.append("Missing title")
    elif len(title) < 20:
        score -= 15
        suggestions.append("Title is too short")
    elif len(title) > 80:
        score -= 10
        suggestions.append("Title exceeds 80 character limit")

    # Check description
    description = listing.get("description", "")
    if not description:
        score -= 40
        suggestions.append("Missing description")
    elif len(description) < 100:
        score -= 20
        suggestions.append("Description is too brief")

    # Check price range
    price_range = listing.get("price_range", "")
    if not price_range:
        score -= 30
        suggestions.append("Missing price range")
    elif "$" not in price_range:
        score -= 10
        suggestions.append("Price range should include currency symbol")

    return {
        "score": max(0, score),
        "suggestions": suggestions
    }