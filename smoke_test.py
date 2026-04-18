"""Smoke test end-to-end : une question, le graphe répond, on valide automatiquement."""

import uuid

from graph.builder import construire_graphe


def main() -> None:
    question = "Quelle est la convention de nommage BB® pour un projet Nuxt ?"
    print(f"❓ Question : {question}\n")

    graphe = construire_graphe(interactif=False)
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    graphe.invoke({"question": question, "iteration": 0}, config=config)
    state = graphe.get_state(config)

    print("📚 Passages récupérés :")
    for i, p in enumerate(state.values.get("passages", []), start=1):
        meta = p.get("metadata", {})
        print(f"  [{i}] {meta.get('source_path')} (distance : {p.get('distance', 0):.3f})")

    print("\n🤖 Réponse finale :")
    print(state.values.get("reponse_finale", "(vide)"))

    rapport = state.values.get("rapport_critique", {})
    print(f"\n🔍 Critic — confiance : {rapport.get('confidence_score', 0):.2f}")
    print(f"   ancrage sources : {rapport.get('source_grounding')}")
    print(f"   sources citées : {rapport.get('sources_cited')}")
    warnings = rapport.get("warnings") or []
    if warnings:
        print(f"   warnings : {warnings}")


if __name__ == "__main__":
    main()
