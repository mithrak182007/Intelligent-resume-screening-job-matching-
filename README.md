# Intelligent Resume Screening and Job Matching

A local Streamlit prototype for comparing resumes against job criteria using transparent text evidence. Built to align with the supplied project brief: resume intake, document parsing, skill extraction, requirement mapping, weighted scoring, evidence explanations, reviewer feedback, privacy-aware handling, and reporting.

## Important responsible-use rule

This application is a **decision-support tool only**. It must not automatically reject, shortlist, or make hiring decisions. The score is a weighted share of criteria with text evidence, **not** a probability of job performance. “No evidence found” means the uploaded text did not contain a recognized term; it does not mean the candidate lacks the skill.

## Features

- Accepts PDF, DOCX, and TXT resumes.
- Extracts text from PDFs and Word documents and flags limited extraction.
- Uses a maintainable synonym dictionary for common skills.
- Shows criterion-by-criterion match status, terms found, and supporting resume sentences.
- Allows role-specific criteria and transparent weights (1–5).
- Stores reviewer status, notes, corrections, score, and evidence summary in local SQLite.
- Keeps an audit-event table for analysis/review/delete events.
- Exports analysis summaries and saved review history as CSV.
- Includes limitations and privacy guidance in the UI.

## Requirements

- Python 3.10 or newer recommended.
- Internet connection only to install Python packages (the app itself processes files locally).

## Setup on Windows (VS Code)

1. Extract the ZIP to a folder.
2. Open the folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, use Command Prompt terminal and run:
   ```bat
   .venv\Scripts\activate.bat
   ```

5. Install dependencies:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. Start the application:

   ```bash
   streamlit run app.py
   ```

7. Streamlit prints a local address (usually `http://localhost:8501`). Open it in your browser.

## How to use

1. Enter the role title and paste the job description.
2. Choose the criteria relevant to the role and adjust weights from 1 (lower importance) to 5 (higher importance).
3. Upload one or more PDF, DOCX, or TXT resumes.
4. Click **Analyze resumes**.
5. Review extraction status, score, each criterion, and the supporting text evidence.
6. Record human review status and notes; click **Save review record**.
7. Download CSV summaries or use **Review history** to export/delete saved records.

## Scoring method

For each criterion:
- A match is recorded if the criterion or one of its listed synonyms occurs in extracted resume text.
- A matched criterion earns its configured weight; an unmatched criterion earns zero.
- Score = `100 × sum(weights for matched criteria) / sum(weights for all criteria)`, rounded to the nearest whole number.

The calculation is intentionally simple and explainable. It does not judge skill proficiency, context, recency, truthfulness, seniority, or actual job performance. Review evidence manually.

## Project structure

```text
intelligent_resume_screening/
├── app.py          # Streamlit user interface and workflow
├── parser.py       # PDF/DOCX/TXT text extraction
├── matcher.py      # synonym matching, evidence extraction, weighted score
├── storage.py      # SQLite review records and audit events
├── requirements.txt
├── README.md
├── sample_job_description.txt
├── sample_resume.txt
└── .gitignore
```

## Sample test data

The included sample files are synthetic and intended only to test the app. Do not use real candidate data unless authorized.

## Privacy and security notes

- Uploaded bytes and extracted resume text are processed in memory and are not written to the database.
- Saved records include filenames, role title, score, criteria evidence summary, reviewer notes/status, and timestamps. Treat the database as confidential.
- The database is local `reviews.db`; the app provides record-level deletion in Review history.
- This prototype has no login or role-based access control. Do not expose it to a public network or use it as a production hiring system.
- Before production use, add authentication/authorization, encryption at rest and in transit, configurable retention/deletion and export workflows, secure deployment, logging minimization, backup/recovery procedures, and legal/accessibility/fairness review.
- Avoid protected attributes and sensitive personal data. Use only data you are permitted to process.

## Known limitations

- Scanned PDFs/image-only files may return little or no text; OCR is not included.
- Matching is based on literal phrases and synonyms, so equivalent wording can be missed and keyword stuffing can create false matches.
- Only English-oriented skill synonyms are included by default.
- Audit events are stored locally, but this prototype does not provide a full audit dashboard.
- The app does not currently support automated job-board integration, candidate email, authentication, multi-user collaboration, or model training.

## Suggested project validation

1. Test with the supplied synthetic sample resume and job description.
2. Test a DOCX and a text-based PDF.
3. Test an empty or scanned PDF and confirm the extraction warning appears.
4. Confirm unmatched criteria say “No supporting statement located” rather than claiming the candidate lacks the skill.
5. Save a review, export history, and delete the saved record.
6. Confirm no automatic rejection occurs.

## GitHub

Initialize version control from this folder:

```bash
git init
git add .
git commit -m "Build intelligent resume screening prototype"
```

Before pushing, verify that `reviews.db`, real resumes, credentials, and private notes are not included. The `.gitignore` excludes the local database and common secret files.
