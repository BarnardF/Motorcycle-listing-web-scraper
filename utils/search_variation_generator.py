def generate_search_variations(search_term):
    """
    Generate search variations for a bike model to improve search results
    
    Args:
        search_term: Original search term (e.g., "Suzuki V-Strom 250")
        
    Returns:
        List of search variations to try, ordered by likelihood
    """
    variations = [search_term]  # Always try original first
    
    parts = search_term.split()
    if len(parts) < 2:
        return variations
    
    brand = parts[0]
    model_parts = parts[1:]
    model_str = ' '.join(model_parts)
    
    # Variation 1: Remove hyphens (V-STROM -> VSTROM)
    no_hyphens = model_str.replace('-', '')
    if no_hyphens != model_str:
        variations.append(f"{brand} {no_hyphens}")
    
    # Variation 2: Just brand + first model word
    if len(model_parts) > 1:
        variations.append(f"{brand} {model_parts[0]}")
    
    # Variation 3: Brand + number only (if there's a number)
    for part in model_parts:
        if any(char.isdigit() for char in part):
            variations.append(f"{brand} {part}")
            break
    
    # Variation 4: Remove "SX", "GS", "X", "SE" suffixes (common model suffixes)
    trimmed = ' '.join([p for p in model_parts if p.upper() not in ['SX', 'GS', 'X', 'SE', 'ABS']])
    if trimmed and trimmed != model_str:
        variations.append(f"{brand} {trimmed}")
    
    # Variation 5: Rearrange if model has separate numbers and names
    # e.g., "G 310" -> also try "G310"
    if len(model_parts) >= 2 and any(p.isdigit() for p in model_parts):
        combined = ''.join(model_parts)
        if combined != model_str:
            variations.append(f"{brand} {combined}")
    
    # Remove duplicates while preserving order
    seen = set()
    unique_variations = []
    for var in variations:
        var_lower = var.lower()
        if var_lower not in seen:
            seen.add(var_lower)
            unique_variations.append(var)
    
    return unique_variations
