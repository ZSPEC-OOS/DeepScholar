# DeepScholar — Phase II–VI Implementation Plan
Status: PLANNED · Updated: 2026-10-20 · Target: production-grade, reproducible literature discovery and formatted citation export.

## Objective
Extend the existing Next.js research workflow (plan → search → rank → verify → synthesize → export) into a comprehensive scholarly evidence-discovery application. A user enters a topic, approves/edit its expanded search strategy, retrieves a large set of genuine research papers, filters and inspects them, and exports a verified bibliography in a chosen style. No synthetic bibliographic records.

## Existing baseline (verify in code before changes)
- Repository: `ZSPEC-OOS/DeepScholar`, active app `deep-research-platform/`.
- README documents DeepSeek search planning, Serper/Crossref search, DOI validation, ranking, report synthesis, and Markdown/BibTeX/JSON/CSV/DOCX/PDF exports.
- Prisma/PostgreSQL stores research sessions; schema already includes `citationStyle`, `sourceCount`, date restrictions, candidates, and verified citations.
- Existing features are documented, not considered production-tested until exercised.
- Do not modify the archived prototype.

## Delivery rules
1. Never invent papers, DOIs, authors, years, journals, or retrieval counts.
2. Maintain `provider`, `provider_id`, raw payload provenance, retrieval timestamp, canonical DOI/PMID/OpenAlex ID, metadata confidence, and source URLs.
3. Separate **discovered**, **deduplicated**, **metadata-verified**, **full-text-accessible**, and **included** counts.
4. Report API failures, rate limits, incomplete pagination, date coverage, and the actual number of records delivered.
5. Preserve backwards-compatible session/export APIs when practical; add migrations with rollback instructions.
6. Do not store API secrets in source code; use Render environment variables.

## Phase II — Search strategy and user controls (P0)
**Purpose:** convert a topic into an inspectable, reproducible search plan.

Tasks:
- [ ] Add structured topic expansion: terminology, synonyms, abbreviations, parent/child concepts, mechanisms, materials/organisms, methods, exclusion terms.
- [ ] Produce 6–12 logically distinct query strings and preserve exact Boolean operators and query provenance; detect near-duplicate queries.
- [ ] Add editable search-plan review before execution; users can delete/add subtopics and include/exclude terms.
- [ ] Add controls for literature depth (e.g. 50/100/250/500 **target** papers), time window, publication types, subject fields, sort, language, and open-access preference.
- [ ] Store the original prompt, model/provider version, finalized queries, parameters, and timestamps.
- [ ] Mark AI-derived expansion as a hypothesis for retrieval, never bibliographic fact.

**Acceptance:** same saved plan can be rerun; expansion is editable; preview shows query count and provider-specific query adaptations; if model API unavailable, user can still run literal/hand-authored queries.

## Phase III — Multi-provider retrieval and metadata normalization (P0)
**Purpose:** expand coverage beyond general web search.

Tasks:
- [ ] Implement first-class connectors for OpenAlex and Crossref; integrate PubMed/NCBI E-utilities for biomedical coverage; optionally Semantic Scholar if quota permits.
- [ ] Build provider adapters with `search(query, cursor, filters)`, normalized result schema, provenance, pagination, retry/backoff, bounded concurrency, timeouts, and transparent partial-failure status.
- [ ] Prefer server-side retrieval; respect API terms, quotas, attribution, user-agent and any required contact email; cache appropriate metadata.
- [ ] Normalize title, complete author list, year/date, journal, volume/issue/pages or article number, publisher, DOI, PMID, URL, abstract, type, citations (source + snapshot date), and open-access links where available.
- [ ] Deduplicate by normalized DOI, then stable identifier and conservative title/year/author matching; retain all matching provider records and conflicts for audit.
- [ ] Paginate to the target count or provider exhaustion. Never claim exhaustive coverage; report searched providers/query counts/pagination boundaries.
- [ ] Separate review articles, original research, preprints, editorials, corrections/retractions and other types.
- [ ] Provide record-level retrievability/access indicators without bypassing paywalls.

**Acceptance:** test fixture with overlapping sources yields one canonical record per paper; dedup precision >= 99% on manually reviewed validation sample; 250 unique records can be retrieved for a sufficiently broad public test topic when provider quotas permit; actual shortfall disclosed.

## Phase IV — Verification, relevance, and evidence assessment (P0)
**Purpose:** prioritize real, relevant work and make its metadata auditable.

Tasks:
- [ ] Resolve DOI metadata against Crossref when available; independently cross-check PMID/OpenAlex references where applicable.
- [ ] Never label a paper “verified” solely because a DOI string matches a regular expression; distinguish `DOI-resolved`, `cross-provider corroborated`, `unverified`, and `conflicting`.
- [ ] Check retraction/correction flags when present in available metadata, display source/date and coverage limitations.
- [ ] Explain ranking with topical relevance, publication type, recency, reproducibility/access to abstract/full text and citation counts (when available); let users switch to chronological/alphabetical sorting.
- [ ] Avoid interpreting citation count as study quality; identify review and preprint status.
- [ ] Offer interactive filtering by year, source, type, availability, term, and verification status, plus individual include/exclude decisions.
- [ ] Preserve citation metadata even when AI synthesis fails.

**Acceptance:** verification labels are traceable to records and source responses; unresolved/contradictory metadata is highlighted instead of silently repaired; selected bibliography contains only real returned records.

## Phase V — Citation style and export engine (P0)
**Purpose:** provide precise publication-ready bibliography output.

Tasks:
- [ ] Support ACS, APA 7, MLA 9, Chicago author-date, IEEE, Vancouver as user-selectable styles; BibTeX and RIS as interchange formats.
- [ ] Use a maintained CSL-compatible formatter and style definitions rather than free-form LLM-generated citations; map normalized metadata to CSL-JSON.
- [ ] Ensure ACS journal abbreviations only when authoritative abbreviations are known; otherwise apply documented fallback and avoid fabricating abbreviations.
- [ ] Format online-first articles, article numbers, missing issues/pages, consortium authors, preprints, >10 authors, and Unicode diacritics.
- [ ] Expose live style preview, copy individual/all, batch export to TXT/Markdown/DOCX/PDF/BibTeX/RIS/CSV/JSON as supported; include URLs/DOIs where style dictates.
- [ ] Generate a machine-readable provenance/search-methods manifest accompanying export, separate from publication bibliography.
- [ ] Regression-test against hand-checked citations for every style, including DOI and missing-field edge cases.

**Acceptance:** >= 95% exact matches against a curated style fixture after documented journal-abbreviation exception handling; no invented field; 500-paper batch export completes within configured service limits.

## Phase VI — Production deployment, scale and observability (P0)
**Purpose:** safely run the app on Render from GitHub.

Tasks:
- [ ] Review existing Next.js build, Prisma database migrations, authentication, and security defaults before deploying.
- [ ] Configure Render web service linked to GitHub `main`; set build/start commands, `NODE_ENV=production`, database URLs and needed API keys **only via secret environment variables**.
- [ ] Set up managed PostgreSQL (existing connection or new instance only after cost/ownership confirmation); verify Prisma migration path and vector extension assumptions if used.
- [ ] Keep provider keys, DeepSeek key, encryption key, and connection strings out of client bundles, repo files and logs.
- [ ] Handle searches as resumable jobs where 100–500 records exceed a single HTTP request time budget; persist checkpoints, progress, last cursor, and failure modes.
- [ ] Add caching, per-user and global quotas, rate limiting, request timeouts, cancellation, job TTL, and measured cost limits.
- [ ] Add smoke tests: health, topic planning, live-provider metadata retrieval, DOI resolution, bibliography export, session restore, and API-error path.
- [ ] Add accessible UI, responsive lists, pagination/virtualization, filter-state URL sharing if safe, and clear empty/partial-results states.
- [ ] Validate deployed URL and deployment logs before calling launch complete.

**Acceptance:** Render deployment healthy; repeatable end-to-end smoke test; explicit failure messages; no leaked secrets; documentation includes local setup, environment variables, migration/runbook, API quotas, and production limitations.

## Sequence and dependencies
| Order | Deliverable | Dependencies | Gate |
|---|---|---|---|
| II | Editable topic-expansion plan | Existing planning API | Saved reproducible queries |
| III | OpenAlex + Crossref + PubMed aggregation | II (may be parallelized) | Real paginated/deduped corpus |
| IV | Metadata checks and selection workflow | III | Transparent verification and rank/filter |
| V | CSL citations and exports | III–IV | Style regression tests pass |
| VI | Render deployment and production jobs | II–V; credentials + database | End-to-end live smoke test |

## Suggested internal code boundaries
- `lib/research/providers/`: provider adapters, typed schemas, retries, rate budgets.
- `lib/research/normalize/`: canonical article model, DOI/title/author dedup.
- `lib/research/plans/`: topic taxonomy, query expansion, saved plans.
- `lib/research/verify/`: identifier resolution and conflict tracking.
- `lib/research/citations/`: CSL normalization, journal abbreviations, exporters.
- `app/api/research/`: existing API workflow adapted incrementally, with compatibility tests.
- `tests/fixtures/`: synthetic provider responses and **real, manually reviewed** citation gold set.

These are proposed directories, not claims about current tree layout.

## Critical risks and mitigations
- **False bibliographic accuracy:** generate references only from retrieved metadata; unresolved fields remain blank/flagged.
- **Coverage bias:** display searched providers, date range, search queries, quotas, and source-specific hit counts.
- **Crossref/OpenAlex/NCBI rate limits:** use pagination, bounded concurrency, caching, contact emails where required, partial results with retry.
- **Ambiguous duplicate titles:** merge conservatively; retain provenance and allow human review.
- **Citation-style edge cases:** deterministic CSL formatting + snapshot/golden tests; do not use AI as the citation formatter.
- **Expensive Render services:** confirm database/service plan before provisioning billable infrastructure.

## Release definition of done
User enters a topic → reviews expanded search plan → searches OpenAlex, Crossref and PubMed (as appropriate) → reviews a sizeable, deduplicated, traceable paper set → selects ACS or another supported style → downloads accurate references with persistent session provenance. All counts reflect actual retrieval; performance, cost, and provider-coverage limits are shown explicitly.

## Credentials and decisions pending
- Confirm how to supply `DATABASE_URL` / `DIRECT_URL`, `DEEPSEEK_API_KEY`, `SERPER_API_KEY` (if retaining web search), and `CROSSREF_MAILTO` in Render secrets.
- Choose whether to use an existing PostgreSQL instance or provision a new one (potentially billable).
- Determine expected concurrent users, retention requirements and whether authenticated research histories must be private.
- Select default citation style (proposed ACS for chemistry) and default paper target (proposed 100).
