# Evaluation of Multi-Agent Systems

A **LangGraph-powered multi-agent framework** for evaluating LLM-based systems using **trajectory matching** and **intent resolution** metrics.

The framework uses a **Supervisor → Worker → Reviewer** architecture with **Google Gemini** as the backend LLM.

---

## Architecture

```text
                         User Query
                             │
                             ▼
                  ┌─────────────────────┐
                  │   Supervisor Agent  │
                  └──────────┬──────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
             ┌─────────────┐   ┌─────────────┐
             │ Work Agent  │   │ Review Agent│
             ├─────────────┤   ├─────────────┤
             │ News Search │   │   Critique  │
             │ PDF Summary │   │ Validation  │
             └──────┬──────┘   └──────┬──────┘
                    │                 │
                    └────────┬────────┘
                             ▼
                  ┌─────────────────────┐
                  │   Evaluation Layer  │
                  ├─────────────────────┤
                  │ Trajectory Matching │
                  │ Intent Resolution   │
                  └─────────────────────┘
```

---

## Features

- Multi-agent orchestration with **LangGraph**
- Supervisor-based agent coordination
- News retrieval and PDF summarization
- Automated content review
- Agent trajectory evaluation
- Multiple trajectory matching strategies
- LLM-based intent resolution scoring
- Configurable evaluation threshold
- Automated tests with `pytest`
- Google Gemini integration

---

## Project Structure

```text
FLLMs-Project/
│
├── main.py
├── pyproject.toml
├── .env
├── .gitignore
├── README.md
│
├── pdfs/
│   ├── IPCC_AR6_SYR_SPM.pdf
│   └── IPCC_AR6_SYR_LongerReport.pdf
│
├── src/
│   └── essay_agent/
│       ├── agents/
│       │   ├── work_agent.py
│       │   └── review_agent.py
│       │
│       ├── ai_eval/
│       │   └── _intent_resolution.py
│       │
│       ├── configs/
│       │   └── app_config.py
│       │
│       ├── graph/
│       │   ├── multi_agent_graph.py
│       │   ├── run_graph.py
│       │   └── evaluation.py
│       │
│       ├── llm/
│       │   └── llm_proxy.py
│       │
│       ├── tools/
│       │   ├── document_tools.py
│       │   ├── news_tools.py
│       │   └── critic_tools.py
│       │
│       └── settings.yaml
│
└── tests/
    ├── test_evaluate_intent_resolution.py
    └── test_trajectory_evaluations.py
```

---

## Requirements

- Python **3.13+**
- [`uv`](https://github.com/astral-sh/uv)
- Google Gemini API key

---

## Installation

### Configure the API Key

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

> Keep `.env` private and do not commit it to the repository.

### Install Dependencies

```bash
uv sync
```

This creates the virtual environment and installs the dependencies defined in `pyproject.toml`.

---

## Usage

### Run the Evaluation Pipeline

```bash
uv run python main.py
```

### Run Tests

```bash
uv run pytest
```

---

## Evaluation

The framework evaluates each test prompt using two complementary evaluation methods:

1. **Trajectory Evaluation**
2. **Intent Resolution Evaluation**

### Trajectory Evaluation

Trajectory evaluation compares the actual execution path of the multi-agent system against a reference trajectory.

| Metric | Description |
|---|---|
| **Unordered Match** | Checks whether actual and reference trajectories contain the same steps regardless of order |
| **Subset Match** | Checks whether the reference trajectory is contained within the actual trajectory |
| **Superset Match** | Checks whether the actual trajectory contains the reference trajectory |
| **Unordered + Overrides** | Performs unordered matching with custom argument comparison rules |

### Intent Resolution

Intent resolution uses an LLM judge to evaluate how well the system understood and fulfilled the user's request.

The score ranges from **1 to 5**:

| Score | Interpretation |
|---:|---|
| **1** | Failed to understand the user's intent |
| **2** | Poor understanding with major issues |
| **3** | Partially resolved the user's intent |
| **4** | Mostly resolved the user's intent |
| **5** | Fully resolved the user's intent |

The default threshold is:

```text
Score >= 3 → PASS
Score <  3 → FAIL
```

---

## Example

For the prompt:

```text
Tell me about black holes in short.
```

The evaluation may produce:

```text
=== TRAJECTORY EVALUATION ===

Unordered Match:              False
Subset Match:                 False
Superset Match:               True
Unordered + Overrides:        False

=== INTENT RESOLUTION ===

Score: 5.0 / 5
Result: PASS
```

A successful **superset match** means that the actual execution trajectory contains all steps present in the reference trajectory, potentially along with additional steps.

---

## Adding Test Prompts

Test prompts are defined in `main.py`.

```python
test_prompts = [
    "Tell me about black holes in short.",
    "Find 5 related news articles on Trump, then review the summary.",
]
```

Add new prompts to this list to evaluate additional scenarios.

### Adding Reference Trajectories

Reference trajectories are defined in:

```text
src/essay_agent/graph/evaluation.py
```

Add the expected trajectory for each new evaluation scenario through `get_reference_outputs()`.

---

## Key Components

### Supervisor Agent

Coordinates the multi-agent workflow and determines which agent should handle each part of the request.

### Work Agent

Handles information-gathering tasks such as:

- News retrieval
- Document processing
- PDF summarization
- Information extraction

### Review Agent

Reviews generated content and provides critique or validation.

### Evaluation Layer

Evaluates the system based on:

- Agent trajectory correctness
- Tool usage
- Intent resolution
- Overall task completion

---

## Evaluation Pipeline

```text
                        Test Prompt
                             │
                             ▼
                    ┌─────────────────┐
                    │   Supervisor    │
                    │      Agent      │
                    └────────┬────────┘
                             │
                ┌────────────┴────────────┐
                ▼                         ▼
        ┌───────────────┐         ┌───────────────┐
        │   Work Agent  │         │  Review Agent │
        └───────┬───────┘         └───────┬───────┘
                │                         │
        ┌───────┴────────┐                │
        ▼                ▼                ▼
   News Search      PDF Summary      Content Review
        │                │                │
        └────────────────┴────────────────┘
                         │
                         ▼
                ┌───────────────────┐
                │  Evaluation Layer │
                └─────────┬─────────┘
                          │
                 ┌────────┴────────┐
                 ▼                 ▼
          ┌──────────────┐  ┌──────────────┐
          │  Trajectory  │  │    Intent    │
          │   Matching   │  │  Resolution  │
          └───────┬──────┘  └──────┬───────┘
                  │                │
                  └───────┬────────┘
                          ▼
                   Final Evaluation
```

---

## Dependencies

| Package | Purpose |
|---|---|
| `langgraph` | Multi-agent workflow orchestration |
| `langgraph-supervisor` | Supervisor agent architecture |
| `langchain-google-genai` | Google Gemini integration |
| `agentevals` | Agent trajectory evaluation |
| `GoogleNews` | News retrieval |
| `pypdf` | PDF text extraction |
| `dynaconf` | Configuration management |
| `pytest` | Automated testing |

---

## Testing

Run the complete test suite with:

```bash
uv run pytest
```

The tests cover:

```text
tests/
├── test_evaluate_intent_resolution.py
└── test_trajectory_evaluations.py
```

---

## Example

For the prompt:

```text
Tell me about black holes in short.
```

The system produces the following evaluation output:

```text
========================================================================================================================
EVALUATING PROMPT 1: Tell me about black holes in short.
========================================================================================================================

Review tool called

=== TRAJECTORY EVALUATION FOR: Tell me about black holes in short. ===

UNORDERED evaluation result:
{'key': 'trajectory_unordered_match', 'score': False, 'comment': None, 'metadata': None}

SUBSET evaluation result:
{'key': 'trajectory_subset_match', 'score': False, 'comment': None, 'metadata': None}

SUPERSET evaluation result:
{'key': 'trajectory_superset_match', 'score': True, 'comment': None, 'metadata': None}

UNORDERED_WITH_OVERRIDES evaluation result:
{'key': 'trajectory_unordered_match', 'score': False, 'comment': None, 'metadata': None}

=== INTENT RESOLUTION EVALUATION ===

Intent Resolution Score: 5.0/5
Result: pass

Explanation:
The assistant correctly understood the user's request for a short explanation
of black holes. It routed the request through its internal multi-agent setup
(supervisor, work agent, and review agent) and successfully produced a clear,
accurate, and concise summary.
```

### Interpreting the Result

The example demonstrates that the system successfully resolved the user's intent with a **5/5** score.

The **Superset Trajectory Match** also returned `True`, meaning the actual execution trajectory contained the expected reference trajectory, potentially along with additional agent or tool steps.

The other trajectory metrics returned `False` because they use stricter matching criteria.

| Metric | Result |
|---|---:|
| Unordered Match | `False` |
| Subset Match | `False` |
| Superset Match | `True` |
| Unordered + Overrides | `False` |
| Intent Resolution | `5.0 / 5` |
| Overall Intent Result | `pass` |

## Future Extensions

Potential extensions include:

- Support for additional LLM providers
- Cost and latency evaluation
- Agent-level performance metrics
- Tool-use accuracy evaluation
- Hallucination detection
- Response quality evaluation
- Larger multi-agent benchmarks
- Human evaluation integration

---
