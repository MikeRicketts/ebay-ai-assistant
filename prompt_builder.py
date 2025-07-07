def build_prompt(details, sold_listings):
    with open('prompt_template.txt', 'r') as file:
        template = file.read()

    sold_listings_text = "\n".join([f"- {listing}" for listing in sold_listings])

    return template.format(
        brand=details['brand'],
        model=details['model'],
        variant=details.get('variant', ''),
        condition=details['condition'],
        notes=details.get('notes', ''),
        sold_listings=sold_listings_text
    )