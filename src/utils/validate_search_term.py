def validate_search_term(search_term, required_format=True):
    """
    Validate search term format
    
    Args:
        search_term: The search term to validate
        required_format: Optional format requirement (e.g., "Brand Model")
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not search_term or not search_term.strip():
        return False, "Search term is empty"
    
    if required_format == "Brand Model":
        parts = search_term.strip().split(maxsplit=1)
        if len(parts) < 2:
            return False, f"Invalid format: '{search_term}' (Expected: Brand Model, e.g., 'Honda CB500X')"
        
    return True, None