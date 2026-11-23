# AI Research Assistant Agent

An agentic research-planning application that turns a topic into a tailored learning report. A rule-driven Planner Agent analyzes topic category, complexity, difficulty, and breadth before selecting tasks. The Research Agent executes only the selected services, then a Validator Agent checks report completeness and scores the result. The Streamlit UI displays both the report and the planner's decision rationale. LLM tasks use Groq's Responses API and the `openai/gpt-oss-20b` model.

## Features

- Plans topic-specific tasks rather than running the same workflow every time.
- Selects future directions and research keywords for research/trend-oriented topics.
- Expands concepts for broad topics and adapts question and roadmap prompts to difficulty.
- Presents topic classification, complexity, difficulty, research depth, selected tasks, and planner rationale.
- Validates selected report sections, detects missing or empty outputs, and reports a quality score with warnings.
- Presents a concise summary, key concepts, research questions, further-study areas, and an actionable learning roadmap when selected.
- Requests JSON output and validates response shapes before displaying them.
- Uses the OpenAI Python SDK with Groq's OpenAI-compatible Responses API endpoint.
- Shows progress, success, and actionable error messages in the Streamlit UI.
- Keeps API keys outside source code and supports dependency injection for offline tests.

## Architecture

```text
Streamlit UI -> PlannerAgent -> ExecutionPlan
                                |
                                v
ResearchAgent -> selected TASK_MAP services -> ReportGenerator
                                                 |
                                          ValidatorAgent
                                                 |
                                        Final report + reasoning
```

See [docs/architecture.md](docs/architecture.md) for component responsibilities and planning rules.

## Installation

Python 3.10 or later is required.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

## Environment Setup

Copy `config/.env.example` to `.env` in the project root (or to `config/.env`) and set your Groq API key:

```text
GROQ_API_KEY=your_api_key_here
```

The application loads environment variables from the process environment, project-root `.env`, or `config/.env`. Never commit a real key.

## Running the Project

From the project root:

```powershell
python run.py
```

Alternatively:

```powershell
python -m streamlit run frontend/app.py
```

Enter a topic and select **Generate Report**. The planner decides which tasks are appropriate before the research agent executes them. The UI displays the decision rationale and validation score. An API or validation error is reported instead of being presented as a complete report.

## Testing

```powershell
python -m pytest
```

Tests use a fake client and do not require a Groq API key or network access. They cover topic classification, dynamic task selection, service dispatch, report validation, and report assembly.

## Screenshots

_Add screenshots of the Streamlit report here._

## Future Enhancements

- Add source retrieval and citations with provenance checks.
- Allow users to export reports to Markdown or PDF.
- Add report history and configurable depth or learner level.
- Support parallel execution of independent subtasks with visible task states.
