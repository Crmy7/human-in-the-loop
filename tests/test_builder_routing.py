"""Tests du routage conditionnel après HITL, sans dépendance LLM."""

import pytest

from graph.builder import router_apres_hitl


def test_approve_question_va_vers_fin():
    etat = {"decision_humaine": "approve", "mode": "question", "iteration": 1}
    assert router_apres_hitl(etat) == "fin"


def test_approve_scaffolding_va_vers_executor():
    etat = {"decision_humaine": "approve", "mode": "scaffolding", "iteration": 1}
    assert router_apres_hitl(etat) == "executor"


def test_edit_question_va_vers_fin():
    etat = {"decision_humaine": "edit", "mode": "question", "iteration": 2}
    assert router_apres_hitl(etat) == "fin"


def test_edit_scaffolding_va_vers_executor():
    etat = {"decision_humaine": "edit", "mode": "scaffolding", "iteration": 2}
    assert router_apres_hitl(etat) == "executor"


def test_reject_sous_max_regenere():
    etat = {"decision_humaine": "reject", "iteration": 1}
    assert router_apres_hitl(etat) == "regenerer"


def test_reject_sous_max_iteration_2_regenere():
    etat = {"decision_humaine": "reject", "iteration": 2}
    assert router_apres_hitl(etat) == "regenerer"


def test_reject_au_max_coupe_la_boucle():
    etat = {"decision_humaine": "reject", "iteration": 3}
    assert router_apres_hitl(etat) == "fin"


def test_reject_au_dela_coupe_aussi():
    etat = {"decision_humaine": "reject", "iteration": 5}
    assert router_apres_hitl(etat) == "fin"


def test_decision_inconnue_leve():
    with pytest.raises(ValueError):
        router_apres_hitl({"decision_humaine": "whatever"})
