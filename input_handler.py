def validate_input(details):
    required_fields = ['brand', 'model', 'condition']
    missing_fields = [field for field in required_fields if not details.get(field)]

    if missing_fields:
        raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

    return True

def process_input(details):
    if validate_input(details):
        return {
            'brand': details['brand'],
            'model': details['model'],
            'variant': details.get('variant', ''),
            'condition': details['condition'],
            'notes': details.get('notes', '')
        }