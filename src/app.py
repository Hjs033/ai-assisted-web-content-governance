import pandas as pd
import streamlit as st

from assessment import assess_content
from ai_analysis import analyze_content
from database import get_audit_records, get_latest_review, init_db, save_review

st.set_page_config(
    page_title="AI-Assisted Content Governance",
    page_icon="🧭",
    layout="wide",
)
init_db()

CRITERIA_VERSION = "1.0"


@st.cache_data
def load_content():
    return pd.read_csv("data/content_sample.csv")


df = load_content()

st.title("AI-Assisted Web Content Governance")
st.caption("Human-in-the-loop content health assessment prototype")

with st.sidebar:
    st.header("Governance Workflow")
    st.write("1. Gather evidence")
    st.write("2. Human provisional assessment")
    st.write("3. AI-assisted analysis")
    st.write("4. Human final decision")
    st.write("5. Record audit rationale")
    st.divider()
    st.caption("Prototype • representative data • no production CMS changes")

    with st.expander("System architecture", expanded=False):
        st.markdown(
            "**Evidence sources** → CMS metadata + web analytics\n\n"
            "**Assessment Engine** → deterministic content-health criteria\n\n"
            "**AI-Assisted Analysis** → qualitative observations\n\n"
            "**Human Review** → final lifecycle decision\n\n"
            "**Audit & Versioning** → rationale, criteria version, prompt version, timestamp"
        )

    with st.expander("Prototype stack", expanded=False):
        st.markdown(
            "- Python\n"
            "- Streamlit\n"
            "- SQLite\n"
            "- pandas\n"
            "- pytest\n"
            "- Git/GitHub"
        )


tab1, tab2, tab3 = st.tabs(["Content Assessment", "Human Review", "Audit History"])

with tab1:
    st.subheader("Content Health Overview")
    assessments = [assess_content(row) for _, row in df.iterrows()]
    assessment_df = pd.DataFrame(assessments)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Content Items", len(df))
    c2.metric("Needs Review", int((assessment_df["system_status"] != "Healthy").sum()))
    c3.metric("Average Health", f"{assessment_df['health_score'].mean():.0f}/100")
    c4.metric("Criteria Version", CRITERIA_VERSION)

    display = assessment_df[
        ["content_id", "title", "health_score", "system_status", "preliminary_recommendation"]
    ].copy()
    display.columns = ["ID", "Title", "Health", "Status", "Recommendation"]
    st.dataframe(display, width="stretch", hide_index=True)

    selected_id = st.selectbox("Select a content item", df["content_id"].tolist())
    row = df[df["content_id"] == selected_id].iloc[0].to_dict()
    result = assess_content(row)
    ai = analyze_content(row, result)

    left, right = st.columns(2)
    with left:
        st.markdown("### Evidence")
        st.write(f"**Title:** {row['title']}")
        st.write(f"**Last updated:** {row['last_updated']}")
        st.write(f"**Page views:** {row['page_views']:,}")
        st.write(f"**Engagement rate:** {row['engagement_rate']:.1%}")
        st.write(f"**Word count:** {row['word_count']:,}")
        st.write(f"**Completeness:** {row['completeness']:.0%}")
        st.write(f"**Duplicate similarity:** {row['duplicate_similarity']:.0%}")

    with right:
        st.markdown("### Deterministic Assessment")
        st.metric("Health score", f"{result['health_score']}/100")
        st.write(f"**Status:** {result['system_status']}")
        st.write(f"**Preliminary recommendation:** {result['preliminary_recommendation']}")
        st.caption(f"**Why:** {result['recommendation_rationale']}")
        for key in ["freshness", "quality", "performance", "duplication", "engagement"]:
            st.progress(result[key] / 100, text=f"{key.title()}: {result[key]:.0f}/100")
        st.caption(
            f"Duplication score reflects content similarity: {row['duplicate_similarity']:.0%} similarity → "
            f"{result['duplication']:.0f}/100 uniqueness score."
        )

    st.markdown("### AI-Assisted Qualitative Analysis")
    st.info(ai["summary"])
    for observation in ai["observations"]:
        st.write("• " + observation)
    st.caption(
        f"AI prompt version: {ai['prompt_version']} • AI is advisory; human review is required."
    )

with tab2:
    st.subheader("Human Review & Governance Decision")
    selected_id = st.selectbox(
        "Content item for review", df["content_id"].tolist(), key="review_id"
    )
    row = df[df["content_id"] == selected_id].iloc[0].to_dict()
    result = assess_content(row)
    ai = analyze_content(row, result)
    previous = get_latest_review(selected_id)

    st.markdown(f"### Evidence summary — {row['title']}")
    e1, e2, e3 = st.columns(3)
    e1.metric("Health", f"{result['health_score']}/100")
    e2.metric("Freshness", f"{result['freshness']}/100")
    e3.metric("Engagement", f"{result['engagement']}/100")

    st.markdown("#### 1. Your independent assessment")
    st.caption("Make your initial assessment before considering the AI-assisted analysis.")
    prior_human = previous["human_assessment"] if previous else "Keep"
    human_options = ["Keep", "Review", "Update", "Consolidate", "Retire"]
    human_assessment = st.radio(
        "Initial governance assessment",
        human_options,
        index=human_options.index(prior_human),
        horizontal=True,
        key=f"human_assessment_{selected_id}",
    )

    st.markdown("#### 2. AI-assisted analysis")
    st.info(ai["summary"])
    for observation in ai["observations"]:
        st.write("• " + observation)
    st.caption(
        f"AI prompt version: {ai['prompt_version']} • AI provides qualitative evidence; it does not make the final decision."
    )

    st.markdown("#### 3. Final governance decision")
    prior_final = previous["final_decision"] if previous else result["preliminary_recommendation"]
    final_decision = st.selectbox(
        "Final decision",
        human_options,
        index=human_options.index(prior_final),
        key=f"final_decision_{selected_id}",
    )

    prior_rationale = previous["rationale"] if previous else ""
    rationale = st.text_area(
        "Reviewer rationale (required)",
        value=prior_rationale,
        placeholder="Explain the evidence and why the final decision is appropriate.",
        key=f"rationale_{selected_id}",
    )

    if previous:
        st.caption(
            f"Most recent saved decision: {previous['final_decision']} on {previous['timestamp']}. "
            "Saving again creates a new audit record rather than deleting the prior record."
        )

    if st.button("Save Human Decision", type="primary"):
        if not rationale.strip():
            st.error("A reviewer rationale is required.")
        else:
            save_review(
                content_id=selected_id,
                system_recommendation=result["preliminary_recommendation"],
                ai_summary=ai["summary"],
                human_assessment=human_assessment,
                final_decision=final_decision,
                rationale=rationale.strip(),
            )
            st.success("Human decision recorded in the audit history.")

with tab3:
    st.subheader("Audit & Version History")
    audit = get_audit_records()
    if audit.empty:
        st.info("No human decisions have been recorded yet.")
    else:
        st.dataframe(audit, width="stretch", hide_index=True)
        st.caption(
            "Audit records preserve the system recommendation, human assessment, final decision, rationale, and configuration versions."
        )
