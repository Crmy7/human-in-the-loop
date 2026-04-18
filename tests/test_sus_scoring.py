"""Tests du scoring SUS (formule Brooke 1996)."""

from evaluation.sus_form import _calculer_score_sus


def test_score_max():
    # Positifs = 5, Négatifs = 1 → score maximal 100
    reponses = [5, 1, 5, 1, 5, 1, 5, 1, 5, 1]
    assert _calculer_score_sus(reponses) == 100.0


def test_score_min():
    # Positifs = 1, Négatifs = 5 → score minimal 0
    reponses = [1, 5, 1, 5, 1, 5, 1, 5, 1, 5]
    assert _calculer_score_sus(reponses) == 0.0


def test_score_neutre():
    # Tout à 3 (neutre) → 50
    reponses = [3] * 10
    assert _calculer_score_sus(reponses) == 50.0
