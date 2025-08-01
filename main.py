import rich_click as click
from dotenv import load_dotenv

from src.llm_client import LLM_CLIENT_REGISTRY

# from src.llm_client import LLM_CLIENT_REGISTRY
from src.models.models import EvaluationConfig
from src.pipeline import EvaluationPipeline

load_dotenv()


@click.command()
@click.option("--csv", required=True, type=click.Path(exists=True), help="Path to input CSV file")
@click.option(
    "--model-provider",
    default="mistral",
    type=click.Choice(list(LLM_CLIENT_REGISTRY.keys())),
    show_default=True,
    help="Provider of the Large Language Model judge.",
)
@click.option("--model-name", required=False, help="Name of the LLM model")
@click.option("--temperature", default=0.0, type=float, show_default=True, help="LLM temperature")
@click.option("--seed", default=42, type=int, show_default=True, help="Random seed")
@click.option("--api-key", required=False, help="API key for the LLM provider")
def main(csv, model_provider, model_name, temperature, seed, api_key):
    config = EvaluationConfig(
        csv=csv,
        model_provider=model_provider,
        model_name=model_name,
        temperature=temperature,
        seed=seed,
        api_key=api_key,
    )

    pipeline = EvaluationPipeline(
        model_provider=config.model_provider,
        model_name=config.model_name,
        temperature=config.temperature,
        seed=config.seed,
        api_key=config.api_key,
    )

    pipeline.run(config.csv)


if __name__ == "__main__":
    main()
