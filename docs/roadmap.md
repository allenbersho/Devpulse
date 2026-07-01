# DevPulse Product Roadmap

## Phase 1: Modular Multi-Agent Reorganization (Current)
- [x] Refactored legacy flat structure into modular directories.
- [x] Implemented Security and Documentation specialist agents.
- [x] Created SQLite persistent context and conversational history memory.
- [x] Exposed FastAPI REST server.
- [x] Built the high-fidelity Streamlit management dashboard.

## Phase 2: Collaboration & Enhanced Analytics
- [ ] **Vector Database Memory**: Add semantic indexing (`vector_memory.py`) utilizing local ChromaDB/FAISS to store and retrieve historical query answers, documentation context, and issues catalog.
- [ ] **Issue Auto-Resolution recommendations**: Give agents the ability to suggest PR changes to resolve specific open issues.
- [ ] **Pull Request compliance audits**: Review open pull requests for structural and coding standard compliance.

## Phase 3: External Integrations (A2A Actions)
- [ ] **External Agent Communication**: Build endpoints allowing external agents to query DevPulse skills and execute operations automatically on its endpoints.
- [ ] **Third-party integrations**: Connect with Jira, Slack, Linear, and email platforms to send weekly health reports.
