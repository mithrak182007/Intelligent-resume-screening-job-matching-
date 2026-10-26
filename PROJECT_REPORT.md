# Project Report: Intelligent Resume Screening and Job Matching

## 1. Abstract
This project provides a transparent decision-support prototype that compares resume text with role-specific criteria. It extracts text from supported document formats, detects skill terms and synonyms, shows supporting statements, calculates an explainable weighted evidence-coverage score, and enables a human reviewer to record notes and corrections.

## 2. Problem statement
Manual resume review can be time-consuming and inconsistent. A tool can help reviewers locate potentially relevant evidence, but automated hiring decisions can be unfair or misleading when information is incomplete. The project therefore focuses on explainability and human review rather than automatic rejection.

## 3. Objectives
- Accept PDF, DOCX, and TXT resumes.
- Extract resume text and report low extraction quality.
- Map role criteria to explicit resume text.
- Normalize common skill synonyms.
- Calculate a transparent score from user-approved weights.
- Show evidence and uncertainty for every criterion.
- Save reviewer notes and maintain a basic audit trail.
- Support CSV export and record deletion.

## 4. System design
**Input layer:** role title, job description, selected criteria, weights, and uploaded resumes.  
**Parsing layer:** PyMuPDF extracts PDF text; python-docx extracts paragraphs and tables; TXT uses UTF-8 decoding.  
**Analysis layer:** a synonym dictionary maps recognized terms to criteria; sentence-level matches provide evidence.  
**Scoring layer:** matched criteria earn their configured weights; the weighted coverage percentage is displayed.  
**Review layer:** human reviewers verify evidence, add notes, and assign a review status.  
**Storage/reporting layer:** SQLite stores review records and audit events; CSV files can be downloaded.

## 5. Algorithm
For each criterion `c`, the app checks whether any recognized term for `c` appears in extracted resume text. If yes, the criterion is marked “Evidence found” and up to three supporting sentences are displayed. Otherwise it is marked “No evidence found” and the UI explains that this does not prove the skill is absent.

Let `w_i` be the configured weight of criterion `i` and `m_i` be 1 when evidence is found, otherwise 0.

`Score = round(100 × Σ(w_i × m_i) / Σ(w_i))`

This score measures text evidence coverage only. It is not a hiring recommendation, proficiency score, or prediction of future performance.

## 6. Technology stack
- Python
- Streamlit for user interface
- PyMuPDF for PDF text extraction
- python-docx for Word document extraction
- pandas for tables and CSV exports
- SQLite for local review storage
- Git for version control

## 7. Privacy and responsible AI
The application processes uploaded file contents in memory and does not save full extracted text. It stores review metadata and notes locally, so the database must be treated as confidential. The prototype does not implement authentication or multi-user access control. Protected attributes should not be included as criteria. Human review is required, and the score must never be used as an automatic rejection rule.

## 8. Testing plan
- Valid PDF, DOCX, and TXT input.
- Unsupported file type validation.
- Empty or scanned PDF extraction warning.
- Exact skill and synonym matching.
- Evidence sentence display.
- Weight changes affect score as expected.
- Review note save and history listing.
- CSV export and record deletion.
- Multiple resume upload and per-file error handling.

## 9. Limitations
Literal matching can miss semantically equivalent expressions and may overvalue keyword stuffing. OCR, authentication, advanced semantic models, production-grade authorization, automated retention policies, and deployment hardening are not included. Results must be interpreted by a qualified human reviewer.

## 10. Future enhancements
- Optional OCR for scanned documents.
- Semantic matching with a locally hosted sentence-embedding model.
- Role-based access control and encrypted storage.
- Configurable retention policies and complete candidate data export/deletion.
- More extensive audit reporting and fairness testing.
- Unit tests, CI workflow, and deployment documentation.

## 11. Conclusion
The prototype demonstrates a complete local workflow for evidence-based resume-to-job matching. Its main design principle is transparency: reviewers can inspect the evidence behind each match, understand what the score means, record corrections, and retain responsibility for decisions.
