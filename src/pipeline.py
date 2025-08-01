import inspect

import pandas as pd
from loguru import logger
from tqdm.rich import tqdm

from src.evaluators import get_evaluators
from src.export import export
from src.llm_client import get_llm_client
from src.models.models import EvaluationResult, RAGEntry, ScoreDetail
from src.models.score_enum import HarmfulnessScore
from src.utils import build_entries


class EvaluationPipeline:
    def __init__(
        self,
        model_provider: str,
        model_name: str,
        temperature: float,
        seed: int,
        api_key: str,
    ):
        self.llm_client = get_llm_client(
            model_provider,
            model=model_name,
            temperature=temperature,
            seed=seed,
            api_key=api_key,
        )
        self.evaluators = get_evaluators(llm_client=self.llm_client)
        self.score_weights = {name: 1.0 for name in self.evaluators}  # default weights that could be a cli option

        # Save the evaluation parameters for the markdown report
        self.evaluation_params = {}
        for k in inspect.signature(self.__init__).parameters.keys():
            # careful to not expose the API key
            if k != "api_key":
                self.evaluation_params[k] = locals()[k]

    def run(self, data: pd.DataFrame):
        logger.info(f"Running evaluation on {len(data)} entries...")
        entries = build_entries(data)
        logger.info("Entries built successfully.")

        results: list[EvaluationResult] = []
        for entry in tqdm(entries, desc="Evaluating CSV entries"):
            result = self.run_evaluators(entry)
            results.append(result)
        logger.info("Evaluation complete. Exporting results...")

        export(
            entries=entries,
            results=results,
            raw_df=data,
            evaluation_params=self.evaluation_params,
            output_dir="reports",
        )
        logger.info("Done")

    def run_evaluators(self, entry: RAGEntry) -> EvaluationResult:
        results: dict[str, ScoreDetail] = {}
        for scoring_name, scorer in self.evaluators.items():
            results[scoring_name] = scorer.score(entry)

        composite_score = self.compute_composite_score(results)
        return EvaluationResult(scores=results, composite=composite_score)

    def compute_composite_score(self, scores: dict[str, ScoreDetail]) -> float:
        """
        Compute the composite score (weighted average) over all individual evaluators' score.
        Parameters
        ----------
        scores : dict[str, float]
           The individual evaluators' scores to be combined.

        Returns
        -------
        float
           The calculated composite score.
        """

        total_weight = sum(self.score_weights.get(k, 1.0) for k in scores)
        weighted_sum = sum(scores[k].normalized_score * self.score_weights.get(k, 1.0) for k in scores)

        harmfulness = scores["harmfulness"]
        factor = {
            HarmfulnessScore.harmful: 0.0,
            HarmfulnessScore.questionable: 0.7,
            HarmfulnessScore.safe: 1.0,
        }[HarmfulnessScore(str(int(harmfulness.score)))]
        return round((weighted_sum / total_weight) * factor, 3)
