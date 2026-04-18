"""Tests de la politique d'écriture sécurisée du nœud executor."""

import os
from pathlib import Path

import pytest

from graph.executor import (
    _dossier_unique,
    _path_est_sur,
    ecrire_scaffolding,
    slugifier,
)


# --------------------------------------------------------------------------- #
# slugifier
# --------------------------------------------------------------------------- #

def test_slugifier_ascii_lowercase_tirets():
    assert slugifier("Mon Projet BB®") == "mon-projet-bb"
    assert slugifier("  espace  multiple  ") == "espace-multiple"
    assert slugifier("déjà accentué") == "deja-accentue"
    assert slugifier("UPPERCASE") == "uppercase"


def test_slugifier_chaine_vide_ou_invalide():
    assert slugifier("") == "projet"
    assert slugifier(None) == "projet"
    assert slugifier("@@@@") == "projet"


# --------------------------------------------------------------------------- #
# _path_est_sur : valide les paths relatifs, rejette les abuses
# --------------------------------------------------------------------------- #

def test_path_valide_relatif(tmp_path):
    assert _path_est_sur("package.json", tmp_path)
    assert _path_est_sur("src/nuxt.config.ts", tmp_path)
    assert _path_est_sur("assets/scss/_variables.scss", tmp_path)


def test_path_rejet_absolu(tmp_path):
    assert not _path_est_sur("/etc/passwd", tmp_path)
    assert not _path_est_sur("/tmp/evil", tmp_path)


def test_path_rejet_traversal(tmp_path):
    assert not _path_est_sur("../etc/passwd", tmp_path)
    assert not _path_est_sur("src/../../../secret", tmp_path)
    assert not _path_est_sur("..", tmp_path)


def test_path_rejet_tilde(tmp_path):
    assert not _path_est_sur("~/.ssh/id_rsa", tmp_path)
    assert not _path_est_sur("~root/evil", tmp_path)


def test_path_rejet_vide(tmp_path):
    assert not _path_est_sur("", tmp_path)
    assert not _path_est_sur(None, tmp_path)  # type: ignore[arg-type]


def test_path_rejet_backslash(tmp_path):
    assert not _path_est_sur("src\\config.ts", tmp_path)


# --------------------------------------------------------------------------- #
# _dossier_unique : suffixe -2, -3… en cas de collision
# --------------------------------------------------------------------------- #

def test_dossier_unique_sans_collision(tmp_path):
    assert _dossier_unique(tmp_path, "test") == tmp_path / "test"


def test_dossier_unique_avec_collision(tmp_path):
    (tmp_path / "test").mkdir()
    assert _dossier_unique(tmp_path, "test") == tmp_path / "test-2"
    (tmp_path / "test-2").mkdir()
    assert _dossier_unique(tmp_path, "test") == tmp_path / "test-3"


# --------------------------------------------------------------------------- #
# ecrire_scaffolding : bout-en-bout avec monkey-patch du dossier base
# --------------------------------------------------------------------------- #

@pytest.fixture
def base_temp(tmp_path, monkeypatch):
    import graph.executor as exe
    monkeypatch.setattr(exe, "SCAFFOLDING_BASE", tmp_path)
    return tmp_path


def test_ecriture_nominale(base_temp):
    scaffolding = {
        "project_name": "Mon Projet Test",
        "description": "Un test",
        "files": [
            {"path": "package.json", "content": "{\"name\":\"test\"}"},
            {"path": "src/nuxt.config.ts", "content": "export default {}"},
        ],
    }
    result = ecrire_scaffolding(scaffolding)
    dossier = Path(result["dossier_ecrit"])
    assert dossier.name == "mon-projet-test"
    assert result["nb_fichiers"] == 2
    assert (dossier / "package.json").read_text() == "{\"name\":\"test\"}"
    assert (dossier / "src/nuxt.config.ts").read_text() == "export default {}"


def test_ecriture_rejette_path_dangereux_sans_rien_ecrire(base_temp):
    scaffolding = {
        "project_name": "evil",
        "files": [
            {"path": "package.json", "content": "ok"},
            {"path": "../../escape.txt", "content": "boom"},
        ],
    }
    with pytest.raises(ValueError, match="Path invalide"):
        ecrire_scaffolding(scaffolding)
    # Atomicité : rien n'a été écrit, le dossier n'existe même pas
    assert not (base_temp / "evil").exists()


def test_ecriture_collision_incremente(base_temp):
    scaffolding = {
        "project_name": "test",
        "files": [{"path": "a.txt", "content": "1"}],
    }
    r1 = ecrire_scaffolding(scaffolding)
    r2 = ecrire_scaffolding(scaffolding)
    assert Path(r1["dossier_ecrit"]).name == "test"
    assert Path(r2["dossier_ecrit"]).name == "test-2"


def test_ecriture_liste_vide_leve(base_temp):
    with pytest.raises(ValueError, match="Aucun fichier"):
        ecrire_scaffolding({"project_name": "x", "files": []})


def test_dry_run_n_ecrit_rien(base_temp):
    scaffolding = {
        "project_name": "dry",
        "files": [{"path": "a.txt", "content": "1"}],
    }
    result = ecrire_scaffolding(scaffolding, dry_run=True)
    assert result["dry_run"] is True
    assert not Path(result["dossier_ecrit"]).exists()
