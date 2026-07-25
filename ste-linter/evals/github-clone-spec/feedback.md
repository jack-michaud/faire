# Simplified Technical English (ASD-STE100) review: baseline.md

54 findings: 6 errors, 48 warnings.

## Sentence length (18)

- line 5: Sentence has 33 words (maximum 25 for descriptive text). Split it into shorter sentences. — `GitForge is a self-hosted, web-based Git hosting platform providing repository m...`
- line 5: Sentence has 25 words (maximum 20 for procedures). Split it if it is an instruction. — `It targets engineering organizations with compliance, data-residency, or air-gap...`
- line 7: Sentence has 22 words (maximum 20 for procedures). Split it if it is an instruction. — `This spec covers the v1 scope: repository hosting over HTTP(S) and SSH, authenti...`
- line 11: Sentence has 21 words (maximum 20 for procedures). Split it if it is an instruction. — `Self-hostable in under 30 minutes  via Docker Compose, with a single Postgres de...`
- line 14: Sentence has 25 words (maximum 20 for procedures). Split it if it is an instruction. — `Horizontally scalable  read path (clones/fetches) separate from the write path (...`
- line 23: Sentence has 24 words (maximum 20 for procedures). Split it if it is an instruction. — `Web/API server  (Go) — stateless HTTP service serving the REST API and rendering...`
- line 25: Sentence has 26 words (maximum 25 for descriptive text). Split it into shorter sentences. — `Repository storage  — bare repos on a shared filesystem (NFS/EFS for small deplo...`
- line 43: Sentence has 25 words (maximum 20 for procedures). Split it if it is an instruction. — `Background workers (same binary,                ) consume a Redis-backed queue f...`
- line 51: Sentence has 22 words (maximum 20 for procedures). Split it if it is an instruction. — `Web-based file browser, blame, and commit history rendered from               / ...`
- line 55: Sentence has 24 words (maximum 20 for procedures). Split it if it is an instruction. — `Auth methods: username/password (bcrypt), SSH keys, personal access tokens (PATs...`
- line 58: Sentence has 25 words (maximum 20 for procedures). Split it if it is an instruction. — `All permission checks centralized in a single         package invoked by both AP...`
- line 79: Sentence has 24 words (maximum 20 for procedures). Split it if it is an instruction. — `Webhooks: per-repo and per-org, HMAC-signed payloads, at-least-once delivery wit...`
- line 98: Sentence has 21 words (maximum 20 for procedures). Split it if it is an instruction. — `Git object data lives entirely outside Postgres, on the repo storage layer; Post...`
- line 102: Sentence has 23 words (maximum 20 for procedures). Split it if it is an instruction. — `Availability : 99.9% target for single-region deployments; API and web servers a...`
- line 104: Sentence has 37 words (maximum 25 for descriptive text). Split it into shorter sentences. — `Security : all traffic TLS-only in production configs; secrets (webhook signing ...`
- line 105: Sentence has 24 words (maximum 20 for procedures). Split it if it is an instruction. — `Backup/DR : nightly Postgres logical backups + continuous WAL archiving; repo st...`
- line 106: Sentence has 21 words (maximum 20 for procedures). Split it if it is an instruction. — `Observability : structured logs (JSON), Prometheus metrics for request latency/q...`
- line 107: Sentence has 23 words (maximum 20 for procedures). Split it if it is an instruction. — `Upgrade path : schema migrations via versioned SQL files applied automatically o...`

## Passive voice (3)

- line 15: Passive voice ("is logged"): use the active voice. Name who or what does the action. — `is logged`
- line 26: Passive voice ("is used"): use the active voice. Name who or what does the action. — `is used`
- line 98: Passive voice ("are backed"): use the active voice. Name who or what does the action. — `are backed`

## Unapproved words (23)

- line 5: Unapproved word "providing": use "give" or "supply". — `providing`
- line 11: Unapproved word "via": use "through" or "by". — `via`
- line 11: Unapproved word "required": use "need" or "must have". — `required`
- line 11: Unapproved word "functionality": use "function(s)". — `functionality`
- line 12: Unapproved word "required": use "need" or "must have". — `required`
- line 43: Unapproved word "via": use "through" or "by". — `via`
- line 43: Unapproved word "initially": use "at the start". — `initially`
- line 48: Unapproved word "Create": use "make". — `Create`
- line 50: Unapproved word "require": use "need" or "must have". — `require`
- line 50: Unapproved word "require": use "need" or "must have". — `require`
- line 50: Unapproved word "require": use "need" or "must have". — `require`
- line 51: Unapproved word "via": use "through" or "by". — `via`
- line 52: Unapproved word "via": use "through" or "by". — `via`
- line 62: Unapproved word "via": use "through" or "by". — `via`
- line 63: Unapproved word "via": use "through" or "by". — `via`
- line 64: Unapproved word "executed": use "do" or "start". — `executed`
- line 65: Unapproved word "Required": use "need" or "must have". — `Required`
- line 65: Unapproved word "via": use "through" or "by". — `via`
- line 74: Unapproved word "via": use "through" or "by". — `via`
- line 79: Unapproved word "via": use "through" or "by". — `via`
- line 80: Unapproved word "via": use "through" or "by". — `via`
- line 104: Unapproved word "via": use "through" or "by". — `via`
- line 107: Unapproved word "via": use "through" or "by". — `via`

## Semicolons (9)

- line 43: Do not use semicolons. Write two short sentences. — `Background workers (same binary,                ) consume a`
- line 48: Do not use semicolons. Write two short sentences. — `Create/fork/mirror repositories; support for bare repo stora`
- line 70: Do not use semicolons. Write two short sentences. — `Comments with reactions; activity timeline (label changes, a`
- line 98: Do not use semicolons. Write two short sentences. — `Git object data lives entirely outside Postgres, on the repo`
- line 102: Do not use semicolons. Write two short sentences. — `Availability : 99.9% target for single-region deployments; A`
- line 103: Do not use semicolons. Write two short sentences. — `Performance : p95 API latency < 200ms for metadata endpoints`
- line 104: Do not use semicolons. Write two short sentences. — `Security : all traffic TLS-only in production configs; secre`
- line 105: Do not use semicolons. Write two short sentences. — `Backup/DR : nightly Postgres logical backups + continuous WA`
- line 107: Do not use semicolons. Write two short sentences. — `Upgrade path : schema migrations via versioned SQL files app`

## -ing sentence openers (1)

- line 69: Sentence starts with the -ing form "Cross-linking". Rewrite with a finite verb (for example: "When you X..." or an imperative). — `Cross-linking:              in PR descriptions auto-closes i`

