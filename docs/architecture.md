# Architecture

## Agent workflow

```text
+------------------+
| User Topic       |
+--------+---------+
         |
         v
+------------------+
| Planner Agent   |
| Analyze topic   |
+--------+---------+
         |
         v
+------------------+
| Classify topic,  |
| level, complexity|
+--------+---------+
         |
         v
+------------------+
| Execution Plan  |
| ordered actions |
+--------+---------+
         |
         v
+------------------+
| Research Agent  |
| TASK_MAP dispatch|
+--------+---------+
         |
         v
+------------------+
| Selected task   |
| services / Groq |
+--------+---------+
         |
         v
+------------------+
| Report Generator|
| organize outputs|
+--------+---------+
         |
         v
+------------------+
| Validator Agent |
| score + warnings|
+--------+---------+
         |
         v
+------------------+
| Final Report    |
| + Agent Reasoning|
+------------------+
         |
         v
+------------------+
| Streamlit UI    |
+------------------+
```

## Components

- **Streamlit UI (`frontend/app.py`)** collects a topic and displays the plan's classification, complexity, difficulty, research depth, selected actions, and rule-based rationale. The final report is rendered by selected section; validation warnings and score remain visible.
- **Planner agent (`backend/planner_agent.py`)** analyzes topic signals before any research task runs. It identifies technical and research-oriented wording, beginner/advanced markers, and broad-scope phrases. It produces an ordered `ExecutionPlan` without making an unnecessary LLM call.
- **Execution plan (`backend/models/execution_plan.py`)** is an immutable, validated representation of topic, category, complexity, difficulty, research depth, selected tasks, and visible rationale.
- **Research agent (`backend/research_agent.py`)** instantiates the services in `TASK_MAP`, runs only the plan's selected actions in order, and connects planning, execution, validation, and report assembly. `backend/agent.py` re-exports the class for earlier imports.
- **Task services (`backend/services/`)** generate summaries, concepts, research questions, roadmaps, future directions, and academic search keywords. Broad topics request additional concepts; difficulty adjusts question and roadmap prompts.
- **Prompts (`backend/prompts.py`)** define task-specific JSON output requirements. The shared `GroqClient` sends requests through the Groq-compatible OpenAI Responses API and validates parsed JSON.
- **Report generator (`backend/report_generator.py`)** maps task outputs into stable report sections and attaches workflow metadata such as selected/executed actions and creation time.
- **Validator agent (`backend/validator_agent.py`)** checks every section required by the plan, detects missing or empty content, emits quality warnings, and computes a deterministic score/status. Validation does not claim that generated content is fact-checked.
- **Settings (`config/settings.py`)** loads API credentials from the environment or dotenv files; secrets are not stored in source code.
- **Tests (`tests/test_agent.py`)** use a queued fake client to exercise decisions, selective task execution, validation, and report shape without a live API key.

## Decision policy

The planner's rationale is generated from explicit, inspectable rules:

- Research/trend/survey/frontier language classifies a topic as research-oriented, selects advanced/deep treatment, and adds future-directions and research-keyword tasks.
- Technical-domain terms classify topics as technical and normally select intermediate difficulty.
- Beginner language selects beginner difficulty, introductory depth, and a simplified roadmap prompt.
- Advanced-level language selects advanced difficulty.
- Broad-scope wording selects exploratory depth, expands concept count, and adds research keywords to help narrow the topic.
- Summary, concepts, questions, and roadmap are the standard task set. Research-specific tasks are added only when their decision rules match.

The UI displays these signals and actions as **Agent Reasoning**. This is a concise explanation of the planner's decision rules, not hidden model chain-of-thought.

## Execution and validation flow

1. Validate and normalize the user's topic.
2. The planner classifies it and returns an ordered execution plan.
3. The research agent dispatches selected actions through `TASK_MAP`; unselected services are not called.
4. The report generator organizes service outputs into report sections.
5. The validator checks required sections according to the plan, calculates a 0-100 quality score, and records warnings.
6. The report generator returns the final report with plan, task, timestamp, and validation metadata.
7. Streamlit shows the plan reasoning and selected report sections.

The model's outputs are suggestions, not sourced research: this version does not retrieve external literature or independently verify factual claims.
