from tools import search_listings, suggest_outfit, create_fit_card
from utils.data_loader import get_example_wardrobe, get_empty_wardrobe

def test_search_returns_results():
    results = search_listings("vintage graphic tee", max_price=50)
    assert isinstance(results, list)
    assert len(results) > 0

def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)
    assert results == []

def test_search_price_filter():
    results = search_listings("jacket", max_price=10)
    assert all(item["price"] <= 10 for item in results)

def test_suggest_outfit_empty_wardrobe():
    results = search_listings("vintage graphic tee", max_price=50)
    output = suggest_outfit(results[0], get_empty_wardrobe())
    assert isinstance(output, str) and len(output) > 0

def test_fit_card_empty_outfit():
    results = search_listings("vintage graphic tee", max_price=50)
    output = create_fit_card("", results[0])
    assert isinstance(output, str) and len(output) > 0