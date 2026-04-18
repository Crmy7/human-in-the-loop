"""Exécute le pipeline sur les 30 questions et calcule les métriques RAGAS + taux de refus."""

import json
import logging
import time
import uuid
from datetime import datetime, timezone

from langchain_anthropic import ChatAnthropic
from langchain_openai import OpenAIEmbeddings
from ragas import EvaluationDataset, SingleTurnSample, evaluate
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.metrics import (
    AnswerRelevancy,
    ContextPrecision,
    ContextRecall,
    Faithfulness,
)

from config import (
    ANTHROPIC_API_KEY,
    DATA_DIR,
    EMBEDDING_MODEL,
    LLM_MODEL,
    OPENAI_API_KEY,
)
from evaluation.dataset import DATASET
from graph.builder import construire_graphe

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("evaluation.ragas_runner")

REFUS_FORMULE = (
    "La documentation interne BB® et les sources publiques indexées ne couvrent pas ce point."
)


def _executer_pipeline(question: dict) -> dict:
    """Exécute le graphe en mode auto sur une question, retourne passages + réponse."""
    graphe = construire_graphe(interactif=False)
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    graphe.invoke({"question": question["question"], "iteration": 0}, config=config)
    state = graphe.get_state(config)
    valeurs = state.values
    return {
        "id": question["id"],
        "category": question["category"],
        "question": question["question"],
        "passages": valeurs.get("passages", []),
        "reponse_finale": valeurs.get("reponse_finale", ""),
        "expected_answer": question["expected_answer"],
        "should_refuse": question["should_refuse"],
    }


def _a_refuse(reponse: str) -> bool:
    return REFUS_FORMULE.lower() in (reponse or "").lower()


def _taux_refus_correct(resultats: list[dict]) -> float:
    hors = [r for r in resultats if r["should_refuse"]]
    if not hors:
        return 0.0
    corrects = sum(1 for r in hors if _a_refuse(r["reponse_finale"]))
    return corrects / len(hors)


def _construire_evaluation_dataset(resultats: list[dict]) -> EvaluationDataset:
    samples: list[SingleTurnSample] = []
    for r in resultats:
        contextes = [p["content"] for p in r["passages"]]
        samples.append(
            SingleTurnSample(
                user_input=r["question"],
                response=r["reponse_finale"],
                retrieved_contexts=contextes,
                reference=r["expected_answer"],
            )
        )
    return EvaluationDataset(samples=samples)


def _sauvegarder(rapport: dict) -> str:
    dossier = DATA_DIR / "eval_results"
    dossier.mkdir(parents=True, exist_ok=True)
    horodatage = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    chemin = dossier / f"ragas_{horodatage}.json"
    chemin.write_text(json.dumps(rapport, ensure_ascii=False, indent=2), encoding="utf-8")
    return str(chemin)


def executer_evaluation() -> dict:
    """Run complet : pipeline sur 30 questions → RAGAS → sauvegarde JSON."""
    logger.info("1/3 — exécution du pipeline sur %d questions", len(DATASET))
    resultats: list[dict] = []
    for i, question in enumerate(DATASET, start=1):
        logger.info("  [%d/%d] %s (%s)", i, len(DATASET), question["id"], question["category"])
        resultats.append(_executer_pipeline(question))
        time.sleep(0.2)

    logger.info("2/3 — calcul des métriques RAGAS")
    llm_eval = LangchainLLMWrapper(
        ChatAnthropic(api_key=ANTHROPIC_API_KEY, model=LLM_MODEL, temperature=0)
    )
    emb_eval = LangchainEmbeddingsWrapper(
        OpenAIEmbeddings(api_key=OPENAI_API_KEY, model=EMBEDDING_MODEL)
    )
    dataset = _construire_evaluation_dataset(resultats)
    metriques = [
        Faithfulness(),
        AnswerRelevancy(),
        ContextPrecision(),
        ContextRecall(),
    ]
    rapport_ragas = evaluate(dataset=dataset, metrics=metriques, llm=llm_eval, embeddings=emb_eval)
    scores = rapport_ragas.to_pandas().to_dict(orient="records")

    taux_refus = _taux_refus_correct(resultats)
    logger.info("3/3 — taux de refus correct hors corpus : %.1f%%", taux_refus * 100)

    rapport = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "llm_model": LLM_MODEL,
        "embedding_model": EMBEDDING_MODEL,
        "nb_questions": len(DATASET),
        "taux_refus_correct_hors_corpus": taux_refus,
        "scores_par_question": scores,
        "details": [
            {
                "id": r["id"],
                "category": r["category"],
                "question": r["question"],
                "reponse_finale": r["reponse_finale"],
                "nb_passages": len(r["passages"]),
                "sources_recuperees": [
                    p.get("metadata", {}).get("source_path") for p in r["passages"]
                ],
            }
            for r in resultats
        ],
    }

    chemin = _sauvegarder(rapport)
    logger.info("rapport sauvegardé : %s", chemin)
    return rapport


if __name__ == "__main__":
    executer_evaluation()
