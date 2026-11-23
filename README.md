# AI Research Assistant Agent

An agentic research-planning application that turns a topic into a tailored learning report. A rule-driven Planner Agent analyzes topic category, complexity, difficulty, and breadth before selecting tasks. The Research Agent executes only the selected services, then a Validator Agent checks report completeness and scores the result. The Streamlit UI displays both the report and the planner's decision rationale. LLM tasks use Groq's Responses API and the `openai/gpt-oss-20b` model.

## Features

- Plans topic-specific tasks rather than running the same workflow every time.
- Selects future directions and research keywords for research/trend-oriented topics.
- Discovers up to five real scholarly papers from Semantic Scholar for technical, research, and emerging-technology topics. Paper metadata and links come from the scholarly API; the LLM does not generate paper citations.
- Expands concepts for broad topics and adapts question and roadmap prompts to difficulty.
- Presents topic classification, complexity, difficulty, research depth, selected tasks, and planner rationale.
- Validates selected report sections, detects missing or empty outputs, and reports a quality score with warnings.
- Presents a concise summary, key concepts, research questions, further-study areas, and an actionable learning roadmap when selected.
- Requests JSON output and validates response shapes before displaying them.
- Uses the OpenAI Python SDK with Groq's OpenAI-compatible Responses API endpoint.
- Shows progress, success, and actionable error messages in the Streamlit UI.
- Keeps API keys outside source code and supports dependency injection for offline tests.

## Research Paper Discovery

The AI Research Assistant can recommend real academic papers using Semantic Scholar to support further study and research. For eligible topics, the agent queries Semantic Scholar's Academic Graph paper-search endpoint and displays returned titles, authors, years, citation counts, abstracts, and paper links. Results are ordered by the API's relevance ranking, with citation count as a secondary signal when relevance scores tie. No paper records are invented by the LLM.

## Architecture

```text
Streamlit UI -> PlannerAgent -> ExecutionPlan -> ResearchAgent
                                                   |
                                           selected TASK_MAP
                                             /           \
                                     LLM services       PaperService
                                          |                 |
                                       Groq API       Semantic Scholar
                                             \           /
                                          ReportGenerator
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
# Optional; use a Semantic Scholar API key if you encounter rate limits.
# SEMANTIC_SCHOLAR_API_KEY=your_semantic_scholar_api_key_here
```

The application loads environment variables from the process environment, project-root `.env`, or `config/.env`. A Semantic Scholar API key is optional and is sent only to Semantic Scholar. Never commit real keys.

## Running the Project

From the project root:

```powershell
python run.py
```

Alternatively:

```powershell
python -m streamlit run frontend/app.py
```

Enter a topic and select **Build my research brief**. The planner decides which tasks are appropriate before the research agent executes them. Eligible topics include real paper recommendations retrieved from Semantic Scholar. The UI displays the decision rationale and validation score. An API or validation error is reported instead of being presented as a complete report.

## Testing

```powershell
python -m pytest
```

Tests use a fake client and do not require a Groq API key or network access. They cover topic classification, dynamic task selection, service dispatch, report validation, and report assembly.

## What Makes This an AI Agent?

The `PlannerAgent` analyzes the user's goal and creates an execution plan. The `ResearchAgent` executes the selected tasks. Some tasks use the LLM for reasoning while others invoke external tools such as Semantic Scholar for scholarly retrieval. The `ValidatorAgent` evaluates output quality and the `ReportGenerator` assembles the final report. The combination of planning, tool selection, execution, validation, and report generation makes the system an AI Agent rather than a simple API call.

## Screenshots

_Add screenshots of the Streamlit report here._

## Future Enhancements

- Add broader source retrieval and evidence-grounded claim summaries.
- Allow users to export reports to Markdown or PDF.
- Add report history and configurable depth or learner level.
- Support parallel execution of independent subtasks with visible task states.
