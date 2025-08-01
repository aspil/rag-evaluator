import importlib
import os

EVALUATOR_REGISTRY = {}


def register_evaluator(name: str):
    def wrapper(cls):
        if name in EVALUATOR_REGISTRY:
            raise ValueError(f"Evaluation score '{name}' is already registered.")
        EVALUATOR_REGISTRY[name] = cls
        return cls

    return wrapper


def get_evaluator(evaluation_score: str, *args, **kwargs):
    if evaluation_score not in EVALUATOR_REGISTRY:
        raise ValueError(f"Unknown evaluation score: '{evaluation_score}'")

    evaluator_cls = EVALUATOR_REGISTRY[evaluation_score]

    return evaluator_cls(*args, **kwargs)


def get_evaluators(*args, **kwargs):
    # _EVALUATOR_REGISTRY = {"relevance": get_evaluator("relevance", *args, **kwargs)}
    return {name: get_evaluator(name, *args, **kwargs) for name in EVALUATOR_REGISTRY}
    # return {name: get_evaluator(name, *args, **kwargs) for name in _EVALUATOR_REGISTRY}


# automatically import any Python files in the evaluators/ directory
for file in sorted(os.listdir(os.path.dirname(__file__))):
    if file.endswith(".py") and not file.startswith("_"):
        file_name = file[: file.find(".py")]
        if file_name != "base.py":
            importlib.import_module("src.evaluators." + file_name)
