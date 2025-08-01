import importlib
import os

LLM_CLIENT_REGISTRY = {}


def register_llm_client(name: str):
    def wrapper(cls):
        if name in LLM_CLIENT_REGISTRY:
            raise ValueError(f"LLM client '{name}' already registered.")
        LLM_CLIENT_REGISTRY[name] = cls
        return cls

    return wrapper


def get_llm_client(provider_name: str, *args, **kwargs):
    if provider_name not in LLM_CLIENT_REGISTRY:
        raise ValueError(f"Unknown LLM provider: '{provider_name}'")

    client_cls = LLM_CLIENT_REGISTRY[provider_name]

    return client_cls(*args, **kwargs)


# automatically import any Python files in the llm_client/ directory
for file in sorted(os.listdir(os.path.dirname(__file__))):
    if file.endswith(".py") and not file.startswith("_"):
        file_name = file[: file.find(".py")]
        if file_name != "base.py":
            importlib.import_module("src.llm_client." + file_name)
