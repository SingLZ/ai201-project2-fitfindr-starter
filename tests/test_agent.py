from agent import run_agent
from utils.data_loader import get_example_wardrobe


def test_agent_happy_path_sets_state():
    session = run_agent(
        query="looking for a vintage graphic tee under $30",
        wardrobe=get_example_wardrobe(),
    )

    assert session["error"] is None
    assert session["search_results"]
    assert session["selected_item"] == session["search_results"][0]
    assert session["outfit_suggestion"]
    assert session["fit_card"]


def test_agent_no_results_stops_early():
    session = run_agent(
        query="designer ballgown size XXS under $5",
        wardrobe=get_example_wardrobe(),
    )

    assert session["error"] is not None
    assert session["search_results"] == []
    assert session["selected_item"] is None
    assert session["outfit_suggestion"] is None
    assert session["fit_card"] is None