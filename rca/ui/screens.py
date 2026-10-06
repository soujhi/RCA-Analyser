"""One function per screen. Screens read and write st.session_state only."""
from __future__ import annotations

import io

import pandas as pd
import streamlit as st

from ..analysis import analyze
from ..contract import CATEGORIES
from ..data.generator import generate
from ..draft import ACTION_RESULTS, DECISIONS, ChainLink, RcaDraft, apply_results, build_draft, engineer_status, sign_off, to_markdown
from ..ingest import load_events
from ..narrate import make_claude_llm, narrate
from . import components as ui
from .charts import timeline_figure
from .graph import build_dot

SAMPLES = (("A", "A · Clear cause", "Line 3, night shift"),
           ("B", "B · Two suspects", "Two things changed together"),
           ("C", "C · Unclear cause", "Nothing obvious in the data"))
EMPTY_HINT = {
    "machine": "Nothing unusual recorded. Worth an inspection if other lanes stay quiet.",
    "material": "No lot or supplier signal found. Worth comparing lot certificates.",
    "method": "No procedure or recipe change recorded. Worth checking changeover records.",
    "measurement": "Nothing recorded. Worth checking sensor calibration before trusting any reading.",
    "people": "No shift or handover signal found. Worth checking handover notes.",
    "environment": "No ambient signal recorded. Worth checking humidity and power logs.",
}


def go_to(step: int) -> None:
    st.session_state.step = step
    st.rerun()


def _load(df: pd.DataFrame, label: str, synthetic: bool) -> None:
    clean, report = load_events(df)
    st.session_state.update(df=clean, report=report, analysis=analyze(clean), label=label,
                            synthetic=synthetic, checked=set(), draft=None)
    go_to(1)


def nav(back: int | None, forward: int | None, forward_label: str = "Continue") -> None:
    left, _, right = st.columns([1, 4, 1])
    if back is not None and left.button("Back", key=f"back_{back}"):
        go_to(back)
    if forward is not None and right.button(forward_label, type="primary", key=f"next_{forward}"):
        go_to(forward)


def screen_start() -> None:
    st.markdown("<span class='eyebrow'>Root cause analysis</span>", unsafe_allow_html=True)
    st.title("Find out what the data supports.")
    st.markdown("<p class='rca-muted'>Load a production event file. We show what happened, sort the evidence, "
                "and put each possible cause on trial. Nothing is ever called a confirmed root cause.</p>",
                unsafe_allow_html=True)
    st.markdown("<div class='section-heading'><div><h2>Try a sample incident</h2></div>"
                "<p class='rca-muted'>Pre-loaded, fictional production events</p></div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for col, (code, title, caption) in zip(cols, SAMPLES):
        with col:
            st.markdown(f"<div class='rca-muted'>{caption}</div>", unsafe_allow_html=True)
            if st.button(title, key=f"sample_{code}", use_container_width=True):
                df, _ = generate(code, seed=1)
                _load(df, f"Sample {code}", True)
    st.markdown("<div class='section-heading' style='margin-top:32px'><div><h2>Or upload your own</h2></div>"
                "<p class='rca-muted'>CSV files up to 25 MB. Your data stays in this session.</p></div>", unsafe_allow_html=True)
    upload = st.file_uploader("Event CSV", type=["csv"], label_visibility="collapsed")
    if upload is not None:
        try:
            _load(pd.read_csv(io.BytesIO(upload.getvalue())), upload.name, False)
        except ValueError as exc:
            st.error(f"{exc} Download the template, or check the column names.")


def screen_data() -> None:
    report = st.session_state.report
    st.markdown("<span class='eyebrow'>Step 2 of 6 · Data check</span>", unsafe_allow_html=True)
    st.title("Is the data ready?")
    st.markdown("<p class='rca-muted'>We checked the structure, timing, and gaps before using any values as evidence.</p>", unsafe_allow_html=True)
    cols = st.columns(4)
    for col, (value, label) in zip(cols, ((str(report.n_rows), "readings"), (report.start[11:16] + " to " + report.end[11:16], "time span"),
                                          (f"{report.cadence_minutes:g} min", "between readings"), (str(len(report.warnings)), "things to know"))):
        col.markdown(ui.stat_tile(value, label), unsafe_allow_html=True)
    if report.warnings:
        for w in report.warnings:
            st.markdown(ui.point("unchecked", w), unsafe_allow_html=True)
    else:
        st.markdown(ui.point("for", "All required columns found and no gaps detected."), unsafe_allow_html=True)
    st.dataframe(st.session_state.df.head(8), use_container_width=True, hide_index=True)
    nav(0, 2)


def screen_timeline() -> None:
    a, df = st.session_state.analysis, st.session_state.df
    headline = next((e.statement for e in a.evidence if e.kind == "incident"), "No clear rise in defects was found.")
    st.markdown("<span class='eyebrow'>Step 3 of 6 · Timeline</span>", unsafe_allow_html=True)
    st.title("What happened")
    st.markdown(f"<div class='finding-callout'><div class='finding-icon'>➜</div><div>"
                f"<p style='margin:0'><strong>{ui.escape(headline)}</strong></p></div></div>", unsafe_allow_html=True)
    ind = a.indicators
    cols = st.columns(4)
    for col, (value, label) in zip(cols, ((str(ind["total_defects"]), "defects in total"), (f"{ind['total_downtime_min']:g} min", "downtime"),
                                          (str(ind["stops"]), "stops"), (", ".join(ind["top_events"]) or "none", "recurring events"))):
        col.markdown(ui.stat_tile(value, label), unsafe_allow_html=True)
    st.plotly_chart(timeline_figure(df, a), use_container_width=True)
    nav(1, 3)


def screen_board() -> None:
    a = st.session_state.analysis
    st.markdown("<span class='eyebrow'>Step 4 of 6 · Evidence</span>", unsafe_allow_html=True)
    st.title("The evidence, sorted")
    st.markdown("<p class='rca-muted'>Six places a cause can hide. Empty lanes are shown on purpose.</p>", unsafe_allow_html=True)
    lanes = list(CATEGORIES)
    for row in (lanes[:3], lanes[3:]):
        for col, category in zip(st.columns(3), row):
            items = [e for e in a.evidence if e.category == category]
            body = "".join(ui.evidence_row(e.id, e.statement) for e in items) or \
                f"<div class='rca-muted'>{ui.escape(EMPTY_HINT[category])}</div>"
            col.markdown(f"<div class='rca-card'>{ui.category_chip(category)}<div style='margin-top:12px'>{body}</div></div>",
                         unsafe_allow_html=True)
    nav(2, 4, "Open the Evidence Court")


def screen_court() -> None:
    a = st.session_state.analysis
    court = a.court
    st.markdown("<span class='eyebrow'>Step 5 of 6 · Evidence Court</span>", unsafe_allow_html=True)
    st.title("Evidence Court")
    st.markdown(ui.verdict_banner(court.verdict, court.reason), unsafe_allow_html=True)
    use_ai = st.toggle("Polish the wording with Claude", value=False,
                       help="Numbers still come from code. Any AI text with an unknown number is rejected.")
    llm = make_claude_llm() if use_ai else None
    if use_ai and llm is None:
        st.caption("No ANTHROPIC_API_KEY found, so the built-in wording is used.")
    for h in court.hypotheses:
        story = narrate(h, llm)
        with st.container():
            st.markdown(f"<div class='rca-card'>{ui.category_chip(h.category)} "
                        f"<h3 style='margin:8px 0'>{ui.escape(h.id)} · {ui.escape(h.title)}</h3>"
                        f"{ui.meter(h.score, h.label)}<p style='margin-top:12px'>{ui.escape(story.text)}</p>"
                        f"<div class='rca-muted'>{'Wording: ' + story.source}"
                        f"{' · ' + ui.escape(story.note) if story.note else ''}</div></div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.markdown("**For**" + "".join(ui.point("for", s) for s in h.supporting) if h.supporting else "**For**<div class='rca-muted'>Nothing yet.</div>", unsafe_allow_html=True)
        c2.markdown("**Against**" + "".join(ui.point("against", s) for s in h.against) if h.against else "**Against**<div class='rca-muted'>Nothing found.</div>", unsafe_allow_html=True)
        st.markdown("**Still unchecked**" + "".join(ui.point("unchecked", line) for line in h.unchecked),
                    unsafe_allow_html=True)
        st.caption("Record what you find in the RCA draft.")
    with st.expander("Cause-and-effect view"):
        st.graphviz_chart(build_dot(a), use_container_width=True)
    nav(3, 5, "Build the RCA draft")


def screen_draft() -> None:
    a = st.session_state.analysis
    if st.session_state.draft is None:
        st.session_state.draft = build_draft(a)
    draft: RcaDraft = st.session_state.draft
    titles = {h.id: h.title for h in a.court.hypotheses}
    st.markdown("<span class='eyebrow'>Step 6 of 6 · Draft</span>", unsafe_allow_html=True)
    st.title("RCA draft")
    st.markdown(ui.notice_banner(), unsafe_allow_html=True)
    draft.problem = st.text_area("Problem", draft.problem)
    st.subheader("Five whys")
    for i, link in enumerate(draft.chain):
        link.answer = st.text_area(link.question, link.answer, key=f"why_{i}")
    st.subheader("Verification actions")
    st.caption("Record what you actually found. A check that finds nothing does not rule a cause out.")
    table = st.data_editor(
        pd.DataFrame(draft.actions), hide_index=True, use_container_width=True, key="actions",
        column_order=("text", "owner", "due", "result", "note", "hypothesis"),
        column_config={"text": st.column_config.TextColumn(disabled=True),
                       "hypothesis": st.column_config.TextColumn(disabled=True),
                       "result": st.column_config.SelectboxColumn("result", options=list(ACTION_RESULTS), required=True)})
    draft.actions = apply_results(table.to_dict("records"))
    st.subheader("What the engineer reported")
    for h in a.court.hypotheses:
        st.markdown(ui.point("unchecked", f"{h.id} {h.title}: {engineer_status(draft, h.id)}"), unsafe_allow_html=True)
    st.subheader("Sign-off")
    if draft.signoff:
        s = draft.signoff
        st.markdown(ui.point("for", f"Signed off by {s['name']} as \"{s['decision']}\" at {s['time']}. "
                                    "This records the engineer's decision, not a software finding."),
                    unsafe_allow_html=True)
    name = st.text_input("Your name", key="signoff_name")
    decision = st.selectbox("Decision", DECISIONS, key="signoff_decision")
    if st.button("Sign off", key="signoff_button"):
        try:
            sign_off(draft, name, decision)
        except ValueError as exc:
            st.error(str(exc))
        else:
            st.rerun()
    st.download_button("Download draft (Markdown)", to_markdown(draft, st.session_state.synthetic, titles),
                       file_name="rca-draft.md", mime="text/markdown", type="primary")
    nav(4, None)


SCREENS = (screen_start, screen_data, screen_timeline, screen_board, screen_court, screen_draft)
