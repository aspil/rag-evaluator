# Automated Evaluation Framework for RAG Answers

This framework provides automated evaluation of assistant responses in Retrieval-Augmented Generation (RAG) systems. It
scores answers across multiple quality dimensions using a large language models (LLMs) as judges.

## Evaluation Dimensions and Scoring Schema

Each assistant response is evaluated on the following dimensions. Each dimension's score is normalized to a 0-1 scale
before computing the composite score.

| Dimension        | Score Range | Weight | Description                                                                                        |
|------------------|-------------|--------|----------------------------------------------------------------------------------------------------|
| Answer Relevance | 0-3         | 1.0    | How well does the assistant’s answer address the user's question?                                  |
| Clarity          | 0-4         | 1.0    | Is the answer easy to read and understand?                                                         |
| Completeness     | 0-2         | 1.0    | Does the answer cover everything the user asked for, or are important parts missing?               |
| Conciseness      | 0-2         | 1.0    | Is the answer as brief as possible without skipping important information or is it too long?       |
| Groundedness     | 0-2         | 1.0    | Is the answer clearly supported by the provided context, or does it include things that weren’t?   |
| Harmfulness      | 0-2         | 1.0    | Is the answer safe or potentially harmful? Checks for dangerous, unethical, or inappropriate info. |

> Prompts are written in order to isolate the semantics of each dimension.

### Score Ranges per Dimension

For the score range of each dimension and a short description of each value, please visit the constant
`SCORE_DESCRIPTIONS` in the [constants.py](src/constants.py) file.

### Rationale behind the evaluation dimensions

Each dimension was defined to capture a distinct aspect of answer quality. Together, they provide a good overall view of
how useful, reliable, and safe a response is:

- **Answer Relevance** checks whether the assistant actually addresses what the user asked. Even a well-written response
  is a miss if it doesn’t match the user’s intent.

- **Clarity** captures how easy the answer is to read and follow. It favors responses that are grammatically sound,
  well-structured, and naturally phrased.

- **Completeness** looks at whether the assistant answered the question in full. Incomplete or partially correct answers
  are rated lower.

- **Conciseness** rewards responses that are brief but informative. It penalizes unnecessary repetition or overly wordy
  answers while preserving key information.

- **Groundedness** is used to catch hallucinations. It measures how well the answer is supported by the provided
  context.

- **Harmfulness** is a safeguard for content safety. If an answer is clearly harmful, the final score is zero. If it's
  questionable, its impact on the final score is increased to show reduced trust.

### Composite Score

The composite score represents an overall assessment of answer quality. It is calculated as a weighted average of the
normalized scores of all evaluators (0-1 scale). For simplicity, all dimensions are weighted equally (1.0).

> If `Harmfulness = 0` (harmful), the composite score is set to **0**. If `Harmfulness = 1` (questionable),
> the dimension gets a higher weight (1.5) in order to penalize ambiguity and reduce the overall score. This ensures the
> system gives priority to safety and trustworthiness.

## Setup

First clone the repository:

```bash
git clone https://github.com/aspil/NLP-take-home---Alexis-Spiliotopoulos.git
cd NLP-take-home---Alexis-Spiliotopoulos.git
```

For ease of use, you may directly use the provided Dockerfile and run the evaluator as follows:

```bash
docker build -t rag-evaluator .
```

Alternatively, install the [uv](https://github.com/astral-sh/uv) package manager, set up a virtual environment and
install dependencies:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh

uv venv --python=3.11
source .venv/bin/activate
uv pip install -r pyproject.toml
```

### Model Providers

#### Local Ollama server

Using Ollama is entirely optional and was used mostly for debugging purposes. However, if you want to use an Ollama
model, follow
these steps:

1. Install Ollama on your machine according to the instructions [here](https://ollama.com/download).
2. Download the model you want to use from [Ollama](https://ollama.com/search), using `ollama pull`. For example:

```bash
ollama pull mistral:7b
```

#### Mistral API

To use the Mistral API you need to have an API key. Once you do, simplt supply it via the `--api-key` CLI option
or the `API_KEY` environment variable (see the *Usage* section below).

## Usage

### Using the Docker image

To use the Docker image that you built in the *Setup* section, simply run:

```bash

# Mistral API
docker run --rm --tty -v $PWD/data:/app/data -v $PWD/reports:/app/reports rag-evaluator \
  --csv data/rag_evaluation_07_2025.csv \
  --model-provider mistral \
  --model-name mistral-medium-latest \
  --api-key YOUR_API_KEY \
  --temperature 0.3 \
  --seed 42

# Ollama
docker run --rm --tty -v $PWD/data:/app/data -v $PWD/reports:/app/reports rag-evaluator \
  --csv data/rag_evaluation_07_2025.csv \
  --model-provider ollama \
  --model-name mistral:7b \
  --temperature 0.3 \
  --seed 42
```

### Using the `main.py` script

```bash
# Mistral API
python main.py --csv data/rag_evaluation_07_2025.csv \
  --model-provider mistral \
  --model-name mistral-medium-latest \
  --api-key YOUR_API_KEY \
  --temperature 0.3 \
  --seed 42
  
# Ollama
python main.py --csv data/rag_evaluation_07_2025.csv \
  --model-provider ollama \
  --model-name mistral:7b \
  --temperature 0.3 \
  --seed 42
```

## CLI Options

| Option             | Description                                                                                             |
|:-------------------|:--------------------------------------------------------------------------------------------------------|
| `--csv`	           | Path to the input CSV file                                                                              |
| `--model-provider` | 	Model provider to use: `ollama` or `mistral`                                                           |
| `--model-name`     | 	Model identifier (e.g. `mistral:7b` for ollama provider, `mistral-medium-latest` for mistral provider) |
| `--api-key`	       | API key for Mistral (or set `API_KEY` environment variable)                                             |
| `--temperature`    | 	Sampling temperature                                                                                   |
| `--seed`           | 	Optional seed for reproducibility                                                                      |

## Outputs

All results are written to the reports/ directory:

- **Markdown Report**: `rag_evaluation_results_<timestamp>.md` Includes evaluation script parameters, evaluation
  criteria, aggregate statistics, and
  detailed per-entry analysis.

- **CSV Export**: `rag_evaluation_results_<timestamp>.csv` Has the original input data plus columns for the individual
  dimension scores and the composite score

## Example

A sample report is included in the `reports/` directory for reference.