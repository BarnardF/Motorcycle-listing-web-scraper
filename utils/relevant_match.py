# Fixes: Better fuzzy matching, HTML parsing improvements, error handling
#ai(Claude) generated - 11 Nov 2025


import re
from difflib import SequenceMatcher
from config.config import MATCH_THRESHOLDS

def normalize_text(text):
    """Normalize text for comparison"""
    if not text:
        return ""
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = ' '.join(text.split())
    return text


def get_word_tokens(text):
    """Extract meaningful words from text"""
    normalized = normalize_text(text)
    words = [w for w in normalized.split() if len(w) > 1]
    return set(words)


def fuzzy_match_score(search_term, listing_title):
    """Calculate fuzzy match score (0.0 to 1.0)"""
    search_norm = normalize_text(search_term)
    title_norm = normalize_text(listing_title)
    
    # Direct substring match (highest priority)
    if search_norm in title_norm or title_norm in search_norm:
        return 1.0
    
    search_words = get_word_tokens(search_term)
    title_words = get_word_tokens(listing_title)
    
    if not search_words:
        return 0.0
    
    # Brand matching (critical)
    search_words_list = list(search_words)
    brand = search_words_list[0] if search_words_list else None
    
    if not brand or brand not in title_words:
        return 0.1
    
    # Model number matching (critical if numbers exist)
    search_numbers = set(re.findall(r'\b\d{2,4}\b', search_norm))
    title_numbers = set(re.findall(r'\b\d{2,4}\b', title_norm))
    
    if search_numbers and not (search_numbers & title_numbers):
        return 0.15
    
    # Jaccard similarity
    intersection = search_words & title_words
    union = search_words | title_words
    jaccard = len(intersection) / len(union) if union else 0.0
    
    # Sequence matching
    sequence_ratio = SequenceMatcher(None, search_norm, title_norm).ratio()
    
    return (jaccard * 0.6) + (sequence_ratio * 0.4)


def is_relevant_match(search_term, listing_title, min_match_ratio=0.435):
    """Check if listing matches search term (fuzzy matching for Gumtree)"""
    score = fuzzy_match_score(search_term, listing_title)
    return score >= min_match_ratio


def is_relevant_autotrader_match(listing_title, search_term):
    """
    Check if AutoTrader listing is relevant to search term
    Focus on model matching since AutoTrader searches by brand
    
    Args:
        listing_title: The listing title from AutoTrader
        search_term: Original search term (e.g., "Harley-Davidson Street 750")
    
    Returns:
        True if relevant, False otherwise
    """
    # Extract model from search term (everything after brand)
    parts = search_term.split(maxsplit=1)
    if len(parts) < 2:
        return True  # Can't validate, allow it
    
    model = parts[1].lower()
    title_lower = listing_title.lower()
    
    # Split model into words and check if key words appear in title
    model_words = model.split()
    
    # For models with numbers, MUST match the number exactly
    # e.g., "Street 750" should NOT match "Street Glide"
    has_number = any(word.replace(',', '').replace('.', '').isdigit() for word in model_words)
    
    if has_number:
        # Extract numbers from both
        search_numbers = set(re.findall(r'\d+', model))
        title_numbers = set(re.findall(r'\d+', listing_title))
        
        # If search has numbers, at least one must appear in title
        if search_numbers and not (search_numbers & title_numbers):
            return False
    
    # Check if key model words appear in title
    # Allow some flexibility but require significant overlap
    matching_words = sum(1 for word in model_words if word in title_lower)
    match_ratio = matching_words / len(model_words) if model_words else 1.0
    
    return match_ratio >= MATCH_THRESHOLDS["autotrader"]