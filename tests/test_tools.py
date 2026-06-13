from tools import create_fit_card, search_listings, suggest_outfit


def test_search_returns_results():
    results = search_listings("vintage graphic tee", size=None, max_price=50)

    assert isinstance(results, list)
    assert len(results) > 0
    assert all(isinstance(item, dict) for item in results)


def test_search_empty_results():
    results = search_listings("designer ballgown", size="XXS", max_price=5)

    assert results == []


def test_search_price_filter():
    results = search_listings("jacket", size=None, max_price=10)

    assert all(item["price"] <= 10 for item in results)


def test_suggest_outfit_empty_wardrobe():
    new_item = {
        "id": "lst_test",
        "title": "Vintage Graphic Tee",
        "description": "Faded black graphic tee.",
        "category": "tops",
        "style_tags": ["vintage", "graphic tee", "grunge"],
        "size": "M",
        "condition": "good",
        "price": 22.0,
        "colors": ["black"],
        "brand": None,
        "platform": "depop",
    }
    wardrobe = {"items": []}

    result = suggest_outfit(new_item, wardrobe)

    assert isinstance(result, str)
    assert result.strip()
    assert "wardrobe is empty" in result.lower()


def test_create_fit_card_empty_outfit():
    new_item = {
        "id": "lst_test",
        "title": "Vintage Graphic Tee",
        "description": "Faded black graphic tee.",
        "category": "tops",
        "style_tags": ["vintage", "graphic tee", "grunge"],
        "size": "M",
        "condition": "good",
        "price": 22.0,
        "colors": ["black"],
        "brand": None,
        "platform": "depop",
    }

    result = create_fit_card("", new_item)

    assert isinstance(result, str)
    assert result.strip()
    assert "error" in result.lower()
    assert "outfit" in result.lower()