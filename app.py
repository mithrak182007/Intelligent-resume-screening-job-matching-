import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime
from parser import extract_text
from matcher import analyze_resume, DEFAULT_SKILLS
from storage import init_db, save_review, list_reviews, delete_review, log_event

st.set_page_config(page_title="Intelligent Resume Screening", page_icon="🧭", layout="wide")
init_db()

st.title("🧭 Intelligent Resume Screening & Job Matching")
st.caption("Decision-support only: transparent criteria, evidence-based matching, and human review. This tool does not reject candidates.")

with st.sidebar:
    st.header("Workflow")
    st.markdown("1. Add a job description\n2. Upload resumes\n3. Review evidence and uncertainty\n4. Record human notes\n5. Export results")
    st.divider()
    st.subheader("Privacy")
    st.write("Files are processed locally by this app. Uploaded file contents are not saved by the app; review summaries and notes are stored in a local SQLite database.")
    st.warning("Use only resumes you are authorized to process. Avoid protected attributes and sensitive personal data.")

tab_analyze, tab_history, tab_about = st.tabs(["Analyze resumes", "Review history", "About & limitations"])

with tab_analyze:
    left, right = st.columns([1, 1])
    with left:
        job_title = st.text_input("Role title", placeholder="e.g., Junior Python Developer")
        job_description = st.text_area("Job description", height=220, placeholder="Paste the job description here...")
        st.markdown("**Role criteria**")
        st.caption("Select criteria to assess. Weights are transparent and normalized during scoring.")
        selected_skills = st.multiselect("Skills / criteria", options=DEFAULT_SKILLS, default=["Python", "SQL", "Git", "Communication"])
        criteria_text = st.text_input("Additional criterion (optional)", placeholder="e.g., REST APIs")
        weights = {}
        if selected_skills:
            cols = st.columns(2)
            for i, skill in enumerate(selected_skills):
                with cols[i % 2]:
                    weights[skill] = st.slider(f"Weight: {skill}", 1, 5, 3, key=f"weight_{skill}")
        uploads = st.file_uploader("Upload resumes (PDF, DOCX, TXT)", type=["pdf", "docx", "txt"], accept_multiple_files=True)
        analyze_btn = st.button("Analyze resumes", type="primary", use_container_width=True)
    with right:
        st.subheader("How scoring works")
        st.markdown("""
        - **Criterion match:** checks for a criterion and its known synonyms in resume text.
        - **Evidence:** shows the sentence that triggered a match, where available.
        - **Score:** weighted share of matched criteria; this is not a probability of job performance.
        - **Missing evidence ≠ evidence of absence:** a resume may omit a skill the candidate has.
        - **Human review required:** use context, verify claims, and document corrections.
        """)
        st.info("The app does not assess age, gender, ethnicity, disability, religion, photo, name, or other protected characteristics. Do not use the score as an automatic screening threshold.")

    if analyze_btn:
        if not job_title.strip() or not job_description.strip():
            st.error("Enter a role title and job description before analyzing.")
        elif not uploads:
            st.error("Upload at least one resume.")
        elif not selected_skills and not criteria_text.strip():
            st.error("Choose at least one criterion.")
        else:
            criteria = list(selected_skills)
            if criteria_text.strip():
                criteria.append(criteria_text.strip())
                weights[criteria_text.strip()] = 3
            results = []
            for uploaded in uploads:
                try:
                    raw = uploaded.getvalue()
                    text, quality = extract_text(uploaded.name, raw)
                    analysis = analyze_resume(text, criteria, weights)
                    results.append({
                        "filename": uploaded.name, "text": text, "quality": quality,
                        "analysis": analysis, "job_title": job_title.strip()
                    })
                except Exception as e:
                    st.error(f"Could not process {uploaded.name}: {e}")
            if results:
                st.session_state["results"] = results
                st.session_state["job_title"] = job_title.strip()
                st.session_state["job_description"] = job_description.strip()
                log_event("analysis_completed", f"{len(results)} resume(s) analyzed for {job_title.strip()}")
                st.success(f"Processed {len(results)} resume(s). Review each result below; ranking is advisory only.")

    if st.session_state.get("results"):
        st.divider()
        st.subheader("Results for human review")
        result_rows = []
        for item in st.session_state["results"]:
            result_rows.append({
                "Resume": item["filename"],
                "Evidence coverage score (%)": item["analysis"]["score"],
                "Criteria matched": f'{item["analysis"]["matched_count"]}/{item["analysis"]["total_count"]}',
                "Extraction status": item["quality"]["status"],
            })
        summary = pd.DataFrame(result_rows).sort_values("Evidence coverage score (%)", ascending=False)
        st.dataframe(summary, use_container_width=True, hide_index=True)
        st.caption("Sorting is for navigation only and must not be used as an automatic rejection rule.")
        csv_bytes = summary.to_csv(index=False).encode("utf-8")
        st.download_button("Download summary CSV", csv_bytes, "resume_match_summary.csv", "text/csv")

        for idx, item in enumerate(st.session_state["results"]):
            a = item["analysis"]
            with st.expander(f'{item["filename"]} — {a["score"]}% evidence coverage', expanded=(idx == 0)):
                st.write(f'**Extraction:** {item["quality"]["status"]} — {item["quality"]["message"]}')
                st.write(f'**Criteria matched:** {a["matched_count"]} of {a["total_count"]}')
                detail = pd.DataFrame(a["criteria"])
                if not detail.empty:
                    st.dataframe(detail, use_container_width=True, hide_index=True)
                st.markdown("**Human review**")
                reviewer = st.text_input("Reviewer identifier (optional)", key=f"reviewer_{idx}")
                notes = st.text_area("Notes / corrections / follow-up questions", key=f"notes_{idx}", height=90)
                override = st.selectbox("Human review status", ["Needs review", "Evidence verified", "Further information needed", "Not assessed"], key=f"status_{idx}")
                if st.button("Save review record", key=f"save_{idx}"):
                    save_review(
                        filename=item["filename"], job_title=item["job_title"],
                        score=a["score"], status=override, reviewer=reviewer,
                        notes=notes, criteria_json=json.dumps(a["criteria"], ensure_ascii=False)
                    )
                    log_event("review_saved", f'{item["filename"]}: {override}')
                    st.success("Review record saved to local database.")

with tab_history:
    st.subheader("Saved review records")
    records = list_reviews()
    if records:
        df = pd.DataFrame(records)
        st.dataframe(df.drop(columns=["criteria_json"], errors="ignore"), use_container_width=True, hide_index=True)
        st.download_button("Export review history CSV", df.drop(columns=["criteria_json"], errors="ignore").to_csv(index=False).encode("utf-8"), "review_history.csv", "text/csv")
        ids = {f'{r["id"]} — {r["filename"]} ({r["created_at"]})': r["id"] for r in records}
        chosen = st.selectbox("Select a record to delete", [""] + list(ids.keys()))
        if chosen and st.button("Delete selected review record", type="secondary"):
            delete_review(ids[chosen])
            log_event("review_deleted", chosen)
            st.success("Record deleted.")
            st.rerun()
    else:
        st.info("No review records have been saved yet.")

with tab_about:
    st.subheader("Project scope")
    st.write("This prototype implements resume intake, text extraction, skill/criterion evidence mapping, transparent weighted scoring, reviewer notes, audit events, and CSV export.")
    st.subheader("Known limitations")
    st.markdown("""
    - Skill matching uses a maintainable synonym dictionary and sentence-level text evidence; it is not a validated hiring model.
    - PDF extraction can fail for scanned/image-only PDFs. OCR is not included in this local prototype.
    - Resume formatting, spelling, language, and writing style can affect what is extracted.
    - Scores are not calibrated predictions and should never be used as the sole basis for a hiring decision.
    - This prototype is not a production access-control system. Deploy only after adding authentication, authorization, encryption, retention policies, security review, and legal/compliance review.
    """)
    st.subheader("Data handling")
    st.write("Uploaded document bytes and extracted full text are held in app memory for the current session and are not persisted. Saved review records contain the filename, role title, score, criterion evidence summary, reviewer status, notes, and timestamp in `reviews.db`. Delete records from Review history or remove the database file when the app is stopped.")
