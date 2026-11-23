# AI Research Assistant Agent — Project Report

## Abstract

The AI Research Assistant Agent is a goal-driven application that turns a research topic into a tailored study report. Unlike a fixed sequence of LLM prompts, it first analyzes and classifies the topic, detects complexity and difficulty, and builds an execution plan. The research agent runs only the tasks chosen by that plan. For technical, research, and emerging-technology topics, it also invokes Semantic Scholar to retrieve real academic paper records. A report validator checks completeness and paper metadata, scores the result, and attaches warnings before the Streamlit interface presents the report and the planner's decision rationale.

## Objectives

- Demonstrate goal-oriented behavior through topic-specific task planning.
- Classify a topic and estimate its complexity, difficulty, and research depth.
- Select research tasks dynamically rather than executing the same calls for every input.
- Generate summaries, concepts, research questions, roadmaps, and optional research-focused sections.
- Retrieve real, relevant scholarly papers from Semantic Scholar without asking the LLM to invent citations.
- Validate report completeness and provide a quality score with warnings.
- Keep orchestration modular, testable, and independent from the Streamlit interface.

## Problem Statement

A basic LLM-powered application can produce useful content but often follows a fixed prompt sequence without deciding what the user's topic requires. It also may not verify that all requested outputs are present. This project addresses that limitation with a planner-executor-validator workflow: the system makes explicit decisions before calling the model and checks the assembled report against the selected plan.

## Methodology

The planner uses transparent topic signals to classify research-oriented, technical, and emerging-technology topics, identify beginner or advanced language, estimate breadth, and set research depth. These decisions create an immutable execution plan containing ordered actions and a concise explanation of the matched rules. The research agent dispatches actions through a task map. Content services use Groq's Responses API, while the papers task calls the Semantic Scholar Academic Graph paper-search API directly. A central report generator organizes outputs and metadata; a deterministic validator checks planned sections, detects missing or empty results, validates paper titles and URLs, and calculates a 0-100 quality score. Tests mock both model responses and the scholarly API so planning, tool execution, and validation can be evaluated offline.

## Architecture Diagram

```text
User Topic
    |
    v
Planner Agent -> Topic Analysis -> Complexity / Category / Difficulty
    |                                      |
    +-----------------> Execution Plan <---+
                           |
                           v
Research Agent -> TASK_MAP -> LLM task services -> Groq API
                           +-> PaperService -> Semantic Scholar API
                           |
                           v
                 Report Generator -> Validator Agent
                           |
                           v
       Final Report + Quality + Agent Reasoning
                           |
                           v
                     Streamlit UI
```

## Workflow

1. The user enters a topic.
2. The planner classifies its category and determines complexity, difficulty, research depth, and task list.
3. The UI can explain the selected tasks and the planner's rule-based rationale.
4. The research agent executes only those selected tasks in plan order.
5. For eligible topics, the paper service queries Semantic Scholar, which returns real paper metadata and API-ranked search results. The LLM is not asked to create paper titles, authors, links, or citations.
6. The report generator collects outputs into named sections and records the paper count and source.
7. The validator checks for missing or empty planned sections, paper titles, and valid URLs; it computes a score and creates warnings.
8. The UI displays the reasoning, selected sections, linked paper cards, and report-quality feedback.

## Decision-Making Examples

- **“Machine Learning”** is classified as technical at intermediate difficulty. It receives the standard summary, concepts, questions, and roadmap tasks, plus the papers task that retrieves relevant scholarly records from Semantic Scholar.
- **“Quantum Computing Research Trends”** is classified as research-oriented and advanced. In addition to the standard tasks, future directions, research keywords, and scholarly paper retrieval are selected.
- **“Beginner guide to machine learning”** receives beginner difficulty and an introductory, simplified roadmap.
- Broad-scope wording increases the number of requested concepts and adds keywords that help narrow the subject.

The displayed reasoning summarizes explicit planner rules; it is not a disclosure of hidden LLM chain-of-thought. The planner is heuristic and does not claim to replace expert classification.

## Technologies Used

- Python 3.10+
- Streamlit for the user interface
- OpenAI Python SDK configured for Groq's Responses API
- Groq model configured as `openai/gpt-oss-20b` by default
- Semantic Scholar Academic Graph paper-search API
- `python-dotenv` for local environment configuration
- Pytest for offline unit tests

## Results

The system returns an execution plan and a structured report containing only the sections requested by the planner. Technical and research topics include up to five relevant paper records returned by Semantic Scholar, including title, authors, year, citation count, abstract, and link. Reports include category, complexity, difficulty, research depth, selected and executed tasks, paper count/source, generation timestamp, validation score/status, and quality warnings. Automated tests cover classifier decisions, distinct task plans, selective execution, report assembly, paper API request/normalization, validation, and Groq-client request setup without network calls.

The quality score measures completeness, basic output presence, and paper title/link validity; it does not assess factual accuracy or scholarly relevance beyond the external search ranking. Retrieved papers are sourced from Semantic Scholar, while generated prose is not independently fact-checked.

## What Makes This an AI Agent?

The `PlannerAgent` analyzes the user's goal and creates an execution plan. The `ResearchAgent` executes the selected tasks. Some tasks use the LLM for reasoning while others invoke external tools such as Semantic Scholar for scholarly retrieval. The `ValidatorAgent` evaluates output quality and the `ReportGenerator` assembles the final report. The combination of planning, tool selection, execution, validation, and report generation makes the system an AI Agent rather than a simple API call.

## Future Scope

- Add evidence retrieval and citations, with source quality and claim-grounding checks.
- Learn planner decisions from explicit user controls or evaluated topic examples.
- Add task-level progress, retries, and user approval before costly tasks.
- Support report export, history, and learner-level configuration.
- Evaluate output quality and planner decisions against a curated benchmark.

## Conclusion

The project demonstrates a stronger agent architecture than a fixed LLM wrapper by separating planning, task selection, execution, validation, and report generation. Explicit decision rules make the behavior inspectable, while the service map and offline tests make it extensible. Future source-retrieval and evaluation work would improve research reliability beyond the current completeness-focused validation.
