import re


def parse_output(text):
    result = {
        "title": "",
        "description": "",
        "price_range": ""
    }

    try:
        match = re.search(r"<START>(.*?)<END>", text, re.DOTALL)
        if not match:
            return result

        content = match.group(1).strip()

        # Extract title
        title_match = re.search(r"Title:\s*(.*?)(?:\n|$)", content)
        if title_match:
            result["title"] = title_match.group(1).strip()

        # Extract description (handles multi-line)
        desc_match = re.search(r"Description:\s*(.*?)(?:Price Range:|$)", content, re.DOTALL)
        if desc_match:
            result["description"] = desc_match.group(1).strip()

        # Extract price range
        price_match = re.search(r"Price Range:\s*(.*?)(?:\n|$)", content)
        if price_match:
            result["price_range"] = price_match.group(1).strip()

        return result
    except Exception as e:
        print(f"Error parsing output: {e}")
        return result