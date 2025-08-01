import re

import pandas as pd

from src.models.models import RAGEntry


def split_fragment_texts(s: str) -> list[str]:
    return [
        line.strip()[3:] if line.strip().startswith(tuple(f"{i}." for i in range(10))) else line.strip()
        for line in s.strip().splitlines()
        if line.strip()
    ]


def split_conversation_history(s: str) -> list[str]:
    return [
        line.strip()[3:] if line.strip().startswith(tuple(f"{i}." for i in range(10))) else line.strip()
        for line in s.strip().splitlines()
        if line.strip()
    ]


def build_entries(df: pd.DataFrame) -> list[RAGEntry]:
    df = df.copy()

    df["Current User Question"] = df["Current User Question"].fillna("").astype(str)
    df["Assistant Answer"] = df["Assistant Answer"].fillna("").astype(str)

    df["Conversation History"] = df["Conversation History"].fillna("")
    df["Fragment Texts"] = df["Fragment Texts"].fillna("")

    return [
        RAGEntry(
            current_user_question=row["Current User Question"],
            conversation_history=row.get("Conversation History", None),
            fragment_texts=row["Fragment Texts"],
            assistant_answer=row["Assistant Answer"],
        )
        for _, row in df.iterrows()
    ]


def format_history(history: str) -> str:
    """
    Formats the conversation history into a better Markdown format.
    This is used to improve the LLM prompt formatting for the conversation history
    and the automated Markdown report.
    """
    if not isinstance(history, str) or not history.strip():
        return "*None*"

    history = history.replace("\\n", "\n")
    lines = history.strip().split("\n")

    formatted_lines = []
    for line in lines:
        # match lines that start with 'User:' or 'Assistant:' and bold these words
        line = re.sub(r"^(User|Assistant):", r"**\1:**", line.strip())
        formatted_lines.append(f"- {line}")

    return "\n".join(formatted_lines)


def format_retrieved_context(context: str) -> str:
    """
    Formats the retrieved context passages into a clean Markdown list format.
    This is used to improve the LLM prompt formatting for the retrieved context
    and the automated Markdown report.
    """
    # handle None or empty context
    if not isinstance(context, str) or not context.strip():
        return "*None*"

    lines = context.strip().split("\n")
    if len(lines) == 1:
        lines = context.strip().split("\\n")

    lines = [line.strip() for line in lines if line.strip()]

    lines = "\n".join(f"{line}" for line in lines)

    return lines
