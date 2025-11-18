"""Unit tests for fuzzy search functionality."""
import pytest
from rapidfuzz import fuzz, process


def test_fuzz_ratio():
    """Test basic fuzzy matching ratio."""
    score = fuzz.ratio("React", "react")
    assert score > 80  # Should be high similarity


def test_fuzz_token_sort_ratio():
    """Test token sort ratio for better matching."""
    score = fuzz.token_sort_ratio("JavaScript", "Java Script")
    assert score > 80


def test_process_extract():
    """Test process.extract for finding best matches."""
    choices = ["React", "Vue.js", "Angular", "Python", "Java"]
    results = process.extract("react", choices, scorer=fuzz.token_sort_ratio, limit=3)
    
    assert len(results) == 3
    # First result should be "React"
    assert results[0][0] == "React"
    assert results[0][1] > 80  # High match score


def test_fuzzy_search_threshold():
    """Test filtering by threshold."""
    choices = ["React", "Vue.js", "Angular", "Python", "Java"]
    query = "react"
    threshold = 75
    
    matches = process.extract(
        query,
        choices,
        scorer=fuzz.token_sort_ratio,
        limit=10,
    )
    
    filtered = [(name, score) for name, score, _ in matches if score >= threshold]
    
    # Should include "React" with high score
    assert any(name == "React" and score >= threshold for name, score in filtered)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

