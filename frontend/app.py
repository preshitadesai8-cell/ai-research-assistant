"""Polished Streamlit interface for the AI Research Assistant Agent."""

from __future__ import annotations

import html
import logging
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.research_agent import ResearchAgent  # noqa: E402

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="AI Research Assistant",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="collapsed",
)

dark_mode = st.session_state.get("dark_mode", False)

st.markdown(
    """
    <style>
    :root {
        --ink: #14213d;
        --muted: #62708a;
        --accent: #4968e8;
        --line: #e7ebf3;
        --surface: #ffffff;
    }
    .stApp {
        background:
            radial-gradient(ellipse at 82% 0%, rgba(107, 130, 255, .09), transparent 34rem),
            #f6f8fc;
        color: var(--ink);
    }
    .block-container {
        max-width: 1160px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }
    [data-testid="stHeader"] { background: transparent; }
    .brand-line {
        display: flex;
        align-items: center;
        gap: .65rem;
        color: #53617b;
        font-size: .83rem;
        font-weight: 700;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin: .2rem 0 1.15rem;
    }
    .brand-mark {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 2rem;
        height: 2rem;
        border-radius: .7rem;
        background: #e9edff;
        color: #405fe0;
        font-size: 1.1rem;
    }
    .hero {
        position: relative;
        overflow: hidden;
        padding: clamp(1.7rem, 4vw, 3.2rem);
        border: 1px solid rgba(255,255,255,.15);
        border-radius: 1.5rem;
        background: linear-gradient(118deg, #172747 0%, #233d73 62%, #425ed1 100%);
        color: white;
        box-shadow: 0 18px 48px rgba(32, 54, 105, .16);
        margin-bottom: 1.35rem;
    }
    .hero::after {
        content: "";
        position: absolute;
        width: 18rem;
        height: 18rem;
        right: -5rem;
        top: -9rem;
        border: 1px solid rgba(255,255,255,.13);
        border-radius: 50%;
        box-shadow: 0 0 0 2.5rem rgba(255,255,255,.035), 0 0 0 5rem rgba(255,255,255,.025);
        pointer-events: none;
    }
    .hero-kicker {
        position: relative;
        z-index: 1;
        color: #c6d1ff;
        font-size: .76rem;
        font-weight: 700;
        letter-spacing: .14em;
        text-transform: uppercase;
        margin-bottom: .8rem;
    }
    .hero h1 {
        position: relative;
        z-index: 1;
        max-width: 760px;
        margin: 0;
        color: #fff;
        font-size: clamp(2rem, 4vw, 3.15rem);
        line-height: 1.08;
        letter-spacing: -.045em;
    }
    .hero p {
        position: relative;
        z-index: 1;
        max-width: 700px;
        margin: 1rem 0 0;
        color: #d7def5;
        font-size: 1.03rem;
        line-height: 1.65;
    }
    .section-heading {
        color: var(--ink);
        font-size: 1.38rem;
        font-weight: 750;
        letter-spacing: -.025em;
        margin: 1.5rem 0 .25rem;
    }
    .section-caption {
        color: var(--muted);
        font-size: .94rem;
        margin: 0 0 1rem;
    }
    .topic-form {
        padding: 1rem 1.25rem .25rem;
        border: 1px solid var(--line);
        border-radius: 1.15rem;
        background: rgba(255,255,255,.9);
        box-shadow: 0 8px 26px rgba(29, 47, 85, .045);
    }
    div[data-testid="stTextArea"] label,
    div[data-testid="stTextInput"] label {
        color: #263754;
        font-weight: 650;
    }
    div[data-testid="stTextArea"] textarea {
        border: 1px solid #dfe5f0;
        border-radius: .75rem;
        background: #fbfcff;
        line-height: 1.55;
        outline: none;
    }
    div[data-testid="stTextArea"] textarea::placeholder {
        color: #78859b !important;
        opacity: 1;
    }
    div[data-testid="stTextArea"] textarea:focus {
        border-color: #7086ec;
        box-shadow: 0 0 0 3px rgba(73,104,232,.12);
    }
    .stButton > button,
    div[data-testid="stFormSubmitButton"] > button {
        min-height: 2.8rem;
        border-radius: .75rem;
        border: 1px solid #405fe0;
        background: linear-gradient(110deg, #4968e8, #6379ed);
        color: white;
        font-weight: 700;
        box-shadow: 0 7px 16px rgba(73,104,232,.2);
        transition: transform .15s ease, box-shadow .15s ease;
    }
    .stButton > button:hover,
    div[data-testid="stFormSubmitButton"] > button:hover {
        border-color: #344fc4;
        color: white;
        transform: translateY(-1px);
        box-shadow: 0 10px 20px rgba(73,104,232,.25);
    }
    .report-title {
        margin: 0;
        color: #14213d;
        font-size: clamp(1.5rem, 3vw, 2rem);
        font-weight: 760;
        letter-spacing: -.035em;
        overflow-wrap: anywhere;
    }
    .eyebrow {
        color: #687895;
        font-size: .75rem;
        font-weight: 750;
        letter-spacing: .12em;
        text-transform: uppercase;
        margin-bottom: .4rem;
    }
    .badge-row { margin-top: .8rem; }
    .badge {
        display: inline-block;
        margin: 0 .38rem .35rem 0;
        padding: .3rem .62rem;
        border: 1px solid #e1e7f2;
        border-radius: 999px;
        background: #f7f9ff;
        color: #445574;
        font-size: .76rem;
        font-weight: 650;
    }
    .report-summary {
        padding: 1.2rem 1.35rem;
        border: 1px solid #e3e8f4;
        border-left: 4px solid #5974e8;
        border-radius: .9rem;
        background: linear-gradient(110deg, #fff, #f8faff);
        color: #35445e;
        font-size: 1.02rem;
        line-height: 1.75;
    }
    .concept-chip {
        display: inline-block;
        margin: .15rem .35rem .4rem 0;
        padding: .48rem .72rem;
        border: 1px solid #e3e9f4;
        border-radius: .7rem;
        background: #f8faff;
        color: #354662;
        font-size: .89rem;
        font-weight: 600;
    }
    .paper-card {
        padding: .85rem 0;
        border-bottom: 1px solid #e8ecf4;
    }
    .paper-card:last-child { border-bottom: 0; }
    .paper-title {
        color: #233554;
        font-size: 1.03rem;
        font-weight: 740;
        line-height: 1.45;
    }
    .paper-meta {
        margin-top: .35rem;
        color: #718099;
        font-size: .82rem;
        line-height: 1.5;
    }
    .paper-why {
        margin-top: .55rem;
        color: #4f5f79;
        font-size: .88rem;
        line-height: 1.5;
    }
    .paper-link {
        display: inline-block;
        margin-top: .55rem;
        color: #4561d5 !important;
        font-size: .85rem;
        font-weight: 700;
        text-decoration: none !important;
    }
    .paper-link:hover { text-decoration: underline !important; }
    .roadmap-step {
        padding: .1rem 0 .7rem .95rem;
        border-left: 2px solid #dfe5f8;
        margin-left: .55rem;
    }
    .roadmap-step:last-child { border-left-color: transparent; }
    .step-number {
        display: inline-flex;
        width: 1.8rem;
        height: 1.8rem;
        align-items: center;
        justify-content: center;
        margin-left: -1.92rem;
        margin-right: .55rem;
        border: 2px solid white;
        border-radius: 50%;
        background: #e9edff;
        color: #405fe0;
        font-size: .78rem;
        font-weight: 800;
        vertical-align: middle;
    }
    .step-title { color: #243552; font-weight: 720; }
    .step-description {
        margin: .4rem 0 0 1.45rem;
        color: #68758c;
        line-height: 1.55;
    }
    .task-pill {
        display: inline-block;
        margin: .2rem .25rem .2rem 0;
        padding: .38rem .6rem;
        border-radius: .55rem;
        background: #eef1ff;
        color: #4057bd;
        font-size: .79rem;
        font-weight: 680;
    }
    div[data-testid="stMetric"] {
        padding: .85rem 1rem;
        border: 1px solid #e7ebf3;
        border-radius: .9rem;
        background: #fff;
        box-shadow: 0 5px 16px rgba(29,47,85,.035);
    }
    div[data-testid="stMetricLabel"] { color: #697791; }
    div[data-testid="stMetricValue"] { color: #1c2d4d; }
    div[data-testid="stExpander"] {
        border: 1px solid #e5eaf3;
        border-radius: .85rem;
        background: rgba(255,255,255,.72);
    }
    .footnote {
        color: #8490a4;
        font-size: .78rem;
        line-height: 1.5;
        margin-top: 1.5rem;
    }
    @media (max-width: 700px) {
        .block-container { padding: 1rem 1rem 2.5rem; }
        .hero { border-radius: 1rem; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

if dark_mode:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(ellipse at 82% 0%, rgba(84, 105, 220, .14), transparent 34rem),
                #101522;
            color: #e8edf8;
            color-scheme: dark;
        }
        .brand-line { color: #b6c1d8; }
        .brand-mark { background: #252f4d; color: #aebcff; }
        .section-heading, .report-title, .step-title,
        div[data-testid="stMarkdownContainer"] h1,
        div[data-testid="stMarkdownContainer"] h2,
        div[data-testid="stMarkdownContainer"] h3,
        div[data-testid="stMarkdownContainer"] h4 {
            color: #edf2ff !important;
        }
        .section-caption, .eyebrow, .footnote,
        .step-description, div[data-testid="stCaptionContainer"] {
            color: #a3aec3 !important;
        }
        div[data-testid="stMarkdownContainer"] p,
        div[data-testid="stMarkdownContainer"] li,
        div[data-testid="stMarkdownContainer"] label,
        div[data-testid="stWidgetLabel"] p {
            color: #d7deec;
        }
        .hero p { color: #d7def5 !important; }
        .hero h1 { color: #fff !important; }
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-color: #30394c !important;
            background-color: #171e2c;
        }
        div[data-testid="stTextArea"] label,
        div[data-testid="stTextInput"] label {
            color: #dce4f4;
        }
        div[data-testid="stTextArea"] textarea {
            border-color: #39445b;
            background: #111827;
            color: #edf2fb;
        }
        div[data-testid="stTextArea"] textarea::placeholder {
            color: #98a5bb !important;
        }
        div[data-testid="stTextArea"] textarea:focus {
            border-color: #8496ff;
            box-shadow: 0 0 0 3px rgba(111,132,255,.2);
        }
        .badge {
            border-color: #39445b;
            background: #202a3c;
            color: #d3dcf1;
        }
        .report-summary {
            border-color: #35415a;
            background: linear-gradient(110deg, #1a2232, #1a2336);
            color: #dce4f3;
        }
        .concept-chip {
            border-color: #39445b;
            background: #202a3c;
            color: #dce5f6;
        }
        .paper-card { border-bottom-color: #35415a; }
        .paper-title { color: #e4ebfa; }
        .paper-meta { color: #a6b2c8; }
        .paper-why { color: #cad4e7; }
        .paper-link { color: #aebcff !important; }
        .roadmap-step { border-left-color: #3a4765; }
        .roadmap-step:last-child { border-left-color: transparent; }
        .step-number {
            border-color: #171e2c;
            background: #2b3656;
            color: #c4ceff;
        }
        .task-pill {
            background: #293454;
            color: #d0d8ff;
        }
        div[data-testid="stMetric"] {
            border-color: #30394c;
            background: #171e2c;
            box-shadow: 0 5px 16px rgba(0,0,0,.12);
        }
        div[data-testid="stMetricLabel"] { color: #aeb9ce; }
        div[data-testid="stMetricValue"] { color: #edf2ff; }
        div[data-testid="stExpander"] {
            border-color: #30394c;
            background: rgba(23,30,44,.82);
        }
        div[data-testid="stExpander"] summary,
        div[data-testid="stExpander"] summary p {
            color: #e5ebf7 !important;
        }
        div[data-testid="stAlert"] p { color: inherit; }
        </style>
        """,
        unsafe_allow_html=True,
    )

brand_col, toggle_col = st.columns([5, 1], vertical_alignment="center")
with brand_col:
    st.markdown(
        '<div class="brand-line"><span class="brand-mark">✳</span> Fieldnotes · Research workspace</div>',
        unsafe_allow_html=True,
    )
with toggle_col:
    st.toggle("Dark mode", key="dark_mode")

st.markdown(
    """
    <section class="hero">
      <div class="hero-kicker">Your AI-powered research companion</div>
      <h1>Turn a big question into a clear path forward.</h1>
      <p>Get a focused topic brief, useful research questions, and a learning roadmap —
      planned around your topic, not generated from a one-size-fits-all template.</p>
    </section>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-heading">Start with a topic</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="section-caption">Be as broad or specific as you like. You can mention a level such as “beginner” or “advanced”.</div>',
    unsafe_allow_html=True,
)

with st.container(border=True):
    with st.form("research_topic_form", border=False):
        topic = st.text_area(
            "What would you like to explore?",
            placeholder="e.g. How machine learning is changing early disease detection",
            height=105,
            label_visibility="visible",
        )
        submitted = st.form_submit_button(
            "✦  Build my research brief",
            type="primary",
            use_container_width=True,
        )


def _safe(value: object) -> str:
    """Escape generated content before embedding it in custom HTML."""
    return html.escape(str(value), quote=True)


def _render_list(items: list[str], *, numbered: bool = False) -> None:
    """Render a concise, consistently spaced list."""
    for index, item in enumerate(items, start=1):
        prefix = f"**{index}.** " if numbered else ""
        st.markdown(f"{prefix}{item}")


def render_agent_reasoning(report: dict[str, Any]) -> None:
    """Render the plan as a compact, transparent agent-analysis panel."""
    plan = report["execution_plan"]
    task_labels = {
        "summary": "Summary",
        "concepts": "Key concepts",
        "questions": "Research questions",
        "roadmap": "Learning roadmap",
        "future_directions": "Future directions",
        "research_keywords": "Research keywords",
        "papers": "Research papers",
    }
    with st.expander("How the agent planned this report", expanded=False):
        left, right = st.columns([1, 1.5], gap="large")
        with left:
            st.markdown("**Topic analysis**")
            st.write(f"**Category** · {plan['topic_type'].replace('_', ' ').title()}")
            st.write(f"**Difficulty** · {plan['difficulty'].title()}")
            st.write(f"**Complexity** · {plan['complexity'].title()}")
            st.write(f"**Research depth** · {plan['research_depth'].title()}")
        with right:
            st.markdown("**Selected execution plan**")
            task_pills = "".join(
                f'<span class="task-pill">✓ {_safe(task_labels[action])}</span>'
                for action in plan["actions"]
            )
            st.markdown(
                f'<div class="badge-row">{task_pills}</div>',
                unsafe_allow_html=True,
            )
            st.markdown("**Decision notes**")
            for reason in plan["reasoning"]:
                st.markdown(f"- {reason}")


def render_report(report: dict[str, Any]) -> None:
    """Render report metadata, quality, selected sections, and agent reasoning."""
    plan = report["execution_plan"]
    sections = report["report"]
    st.markdown("---")
    title_col, quality_col = st.columns([3, 1], vertical_alignment="center")
    with title_col:
        st.markdown('<div class="eyebrow">Research brief</div>', unsafe_allow_html=True)
        st.markdown(
            f'<h2 class="report-title">{_safe(report["topic"])}</h2>',
            unsafe_allow_html=True,
        )
        badges = "".join(
            [
                f'<span class="badge">{_safe(plan["topic_type"].title())}</span>',
                f'<span class="badge">{_safe(plan["difficulty"].title())} level</span>',
                f'<span class="badge">{_safe(plan["research_depth"].title())} depth</span>',
            ]
        )
        st.markdown(
            f'<div class="badge-row">{badges}</div>',
            unsafe_allow_html=True,
        )
    with quality_col:
        st.metric("Quality check", f"{report['quality_score']} / 100", report["quality_status"].replace("_", " ").title())

    st.progress(report["quality_score"] / 100)
    if report["quality_warnings"]:
        for warning in report["quality_warnings"]:
            st.warning(warning)
    else:
        st.caption("Completeness checks passed for all selected report sections.")

    st.markdown('<div class="section-heading">Your research brief</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="report-summary">{_safe(sections["summary"])}</div>',
        unsafe_allow_html=True,
    )

    primary_left, primary_right = st.columns(2, gap="large")
    with primary_left:
        with st.container(border=True):
            st.markdown("#### Key concepts")
            chips = "".join(
                f'<span class="concept-chip">{_safe(concept)}</span>'
                for concept in sections["key_concepts"]
            )
            st.markdown(chips, unsafe_allow_html=True)

        if "future_directions" in sections:
            with st.container(border=True):
                st.markdown("#### Future directions")
                _render_list(sections["future_directions"])

    with primary_right:
        with st.container(border=True):
            st.markdown("#### Questions to investigate")
            _render_list(sections["research_questions"], numbered=True)

        if "research_keywords" in sections:
            with st.container(border=True):
                st.markdown("#### Search keywords")
                keywords = "".join(
                    f'<span class="concept-chip">{_safe(keyword)}</span>'
                    for keyword in sections["research_keywords"]
                )
                st.markdown(keywords, unsafe_allow_html=True)

    with st.expander(
        "📚 Recommended Research Papers",
        expanded=bool(sections.get("recommended_papers")),
    ):
        if "papers" not in plan["actions"]:
            st.info(
                "The planner did not select paper discovery for this topic. "
                "Try a technical, research, or emerging-technology topic to include scholarly papers."
            )
        elif report["metadata"]["task_errors"].get("papers"):
            st.warning(
                "Paper discovery was selected, but Semantic Scholar could not be reached: "
                f"{report['metadata']['task_errors']['papers']}"
            )
        elif not sections.get("recommended_papers"):
            st.info("Semantic Scholar returned no papers for this topic.")
        else:
            st.caption(
                f"Retrieved from Semantic Scholar · "
                f"{report['metadata']['papers_found']} paper(s)"
            )
            for paper in sections.get("recommended_papers", []):
                with st.container(border=True):
                    st.markdown(
                        f'<div class="paper-title">{_safe(paper["title"])}</div>',
                        unsafe_allow_html=True,
                    )
                    authors = ", ".join(paper["authors"]) if paper["authors"] else "Authors unavailable"
                    year = paper["year"] if paper["year"] is not None else "Year unavailable"
                    st.markdown(
                        f'<div class="paper-meta">{_safe(authors)} · {_safe(year)} · '
                        f'{paper["citation_count"]:,} citations</div>',
                        unsafe_allow_html=True,
                    )
                    if paper["abstract"]:
                        preview = paper["abstract"]
                        if len(preview) > 500:
                            preview = preview[:497].rsplit(" ", 1)[0] + "..."
                        st.write(preview)
                    else:
                        st.caption("Abstract unavailable from Semantic Scholar.")
                    st.markdown(
                        f'<div class="paper-why">{_safe(paper["why_it_matters"])}</div>',
                        unsafe_allow_html=True,
                    )
                    paper_url = paper["url"]
                    try:
                        parsed_url = urlsplit(paper_url)
                        valid_url = (
                            parsed_url.scheme in {"http", "https"}
                            and bool(parsed_url.hostname)
                            and parsed_url.port != 0
                        )
                    except ValueError:
                        valid_url = False
                    if valid_url:
                        st.markdown(
                            f'<a class="paper-link" href="{_safe(paper["url"])}" '
                            'target="_blank" rel="noopener noreferrer">Open paper ↗</a>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.caption("Paper link unavailable.")

    optional_left, optional_right = st.columns([1, 2], gap="large")
    if "further_study" in sections:
        with optional_left:
            with st.container(border=True):
                st.markdown("#### Further study")
                _render_list(sections["further_study"])

    if "learning_roadmap" in sections:
        with optional_right:
            with st.container(border=True):
                st.markdown("#### Learning roadmap")
                for index, step in enumerate(sections["learning_roadmap"], start=1):
                    st.markdown(
                        f'<div class="roadmap-step"><span class="step-number">{index}</span>'
                        f'<span class="step-title">{_safe(step["step"])}</span>'
                        f'<div class="step-description">{_safe(step["description"])}</div></div>',
                        unsafe_allow_html=True,
                    )

    render_agent_reasoning(report)
    st.markdown(
        '<div class="footnote">AI-generated study guidance is a starting point, not a substitute '
        'for reviewing primary sources. Recommended papers are retrieved from Semantic Scholar; '
        'generated study guidance is not independently source-verified.</div>',
        unsafe_allow_html=True,
    )


if submitted:
    if not topic.strip():
        st.error("Enter a research topic to build your brief.")
        st.session_state.pop("research_report", None)
    else:
        try:
            with st.spinner("Analyzing the topic and building a tailored research plan..."):
                st.session_state["research_report"] = ResearchAgent().create_report(topic)
            st.toast("Your research brief is ready.", icon="✅")
        except (ValueError, RuntimeError) as exc:
            st.session_state.pop("research_report", None)
            logger.exception("Could not generate research report")
            st.error(str(exc))
        except Exception:
            st.session_state.pop("research_report", None)
            logger.exception("Unexpected error while generating research report")
            st.error("An unexpected error occurred. Check the application logs and try again.")

if "research_report" in st.session_state:
    render_report(st.session_state["research_report"])
else:
    st.markdown(
        """
        <div class="footnote">
          <strong>How it works:</strong> The planner classifies your topic and selects focused tasks.
          The research agent executes that plan, checks the output, and assembles your brief.
        </div>
        """,
        unsafe_allow_html=True,
    )
