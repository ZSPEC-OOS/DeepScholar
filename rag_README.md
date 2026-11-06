# RAG Studio — compact scientific writing workspace

A single Flask web service with an OpenAI-hosted persistent vector store. Upload multiple PDFs, search their contents, generate sourced drafts, edit locally, and export Markdown.

## Render configuration
- Runtime: Python
- Build command: `pip install -r rag_requirements.txt`
- Start command: `gunicorn --bind 0.0.0.0:$PORT rag_app:app --workers 1 --timeout 240`
- Environment variables (in Render dashboard, **never commit secrets**):
  - `APP_PASSWORD`: a long unique password; browser uses HTTP Basic authentication.
  - `OPENAI_API_KEY`: OpenAI platform secret key from https://platform.openai.com/api-keys
  - `OPENAI_MODEL` (optional): `gpt-4.1-mini`

## Workflow
1. Launch the web app, sign in using any username and APP_PASSWORD as the password.
2. Select **Create / reconnect library**. The generated `vs_...` ID is kept in browser localStorage.
3. Select PDF files and choose **Upload and index**. Uploads are sequential and can take time.
4. Search references; generate text with the assistant; review, append, or replace content in the editor.
5. Export your draft as Markdown. Local autosave is device/browser-specific.

## Operational limitations
- OpenAI API billing is independent of ChatGPT subscription; hosted file-search usage/storage has separate fees.
- Uploaded PDFs reside in OpenAI files/vector storage. Verify policy and licensing before uploading confidential/copyrighted materials.
- This MVP stores document text and the library ID in browser localStorage, not a server database. Export backups. If browser storage is cleared, reconnect with your saved `vs_...` ID.
- No OCR pipeline, document versioning, role-based accounts, DOI metadata extraction or guaranteed page-perfect citations.
- File indexing results may lag; verify citations and scientific content.
- Keep the deployment private by using an unguessable password. Browser Basic credentials require HTTPS (Render uses HTTPS). Prefer stronger authentication for multi-user use.
- The existing DeepScholar main branch is not modified; this deployment uses the dedicated `rag-studio-mvp` branch.
