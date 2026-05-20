# Render import & setup helper

This file documents steps and provides a checklist to import `render.yaml` and configure services.

Steps:

1. Ensure your repository is pushed to GitHub and accessible to Render.
2. In Render Dashboard -> New -> Import from Repo -> select your repository.
3. Render will detect `render.yaml`. Follow the import wizard to create:
   - Managed Postgres database (stores `DATABASE_URL`)
   - Web service for backend (uses `backend/Dockerfile`)
   - Static site for frontend (build `frontend-react` -> `dist`)
4. In each service's Environment tab, set the following variables (use values from `.env.render`):
   - `ADMIN_TOKEN`
   - `OPENAI_API_KEY` (only if enabling LLM)
   - `KNOWLEDGE_BASE_PATH`
   - `DATABASE_URL` (from Managed Postgres)
   - `VITE_API_BASE_URL` (frontend pointing to backend URL)
5. Enable Auto Deploy (On Push) for services as desired.

Optional: Use Render CLI / API

If you want to automate import via Render API, you'll need a Render API key. For security, store it in GitHub Secrets and use CI workflows to call the Render API.
