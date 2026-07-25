# GitForge Technical Specification

## Overview

GitForge is a self-hosted, web-based Git hosting platform providing repository management, code review, and issue tracking for teams that need to run their own infrastructure instead of relying on GitHub, GitLab, or Bitbucket. It targets engineering organizations with compliance, data-residency, or air-gapped deployment requirements, and offers a single-binary or Docker Compose deployment model to keep operational overhead low.

This spec covers the v1 scope: repository hosting over HTTP(S) and SSH, authentication/permissions, pull requests, issues, and the public API. Out of scope for v1: CI/CD runners, wikis, package registries, and federation between GitForge instances.

## Goals

- **Self-hostable in under 30 minutes** via Docker Compose, with a single Postgres dependency and no external services required for core functionality.
- **Git-native compatibility**: works with stock `git` CLI over SSH and HTTPS, no custom client required.
- **Familiar UX** for engineers coming from GitHub: PRs, inline diff comments, issue linking, branch protection.
- **Horizontally scalable** read path (clones/fetches) separate from the write path (pushes, API), so a single instance can grow from 10 to 10,000 repos.
- **Auditable**: every permission change, merge, and force-push is logged.

Non-goals for v1: multi-region replication, built-in CI, marketplace/app ecosystem.

## Architecture

GitForge is split into four services behind a reverse proxy:

1. **Web/API server** (Go) — stateless HTTP service serving the REST API and rendering the web UI (server-rendered + a React SPA for PR/diff views). Scales horizontally behind a load balancer.
2. **Git daemon** — handles `git-upload-pack`/`git-receive-pack` over SSH (custom SSH server embedding `golang.org/x/crypto/ssh`) and smart HTTP. Talks to a shared repository store.
3. **Repository storage** — bare repos on a shared filesystem (NFS/EFS for small deployments) or per-shard local disk with a repo→shard mapping table for larger deployments. Git objects are never stored in Postgres.
4. **Postgres** — system of record for users, orgs, permissions, PRs, issues, comments, and webhooks. Redis is used for job queues (webhook delivery, PR diff pre-computation) and session/rate-limit caching.

```
Client (git/ssh, git/https, browser)
        │
   Reverse Proxy (TLS termination)
   ┌────┴─────┐
   │          │
Web/API    Git Daemon
   │          │
   └────┬─────┘
        │
  Repo Storage (bare repos)
        │
   Postgres + Redis
```

Background workers (same binary, `--mode=worker`) consume a Redis-backed queue for async work: webhook delivery, merge-conflict pre-check, search indexing (via Postgres full-text initially; pluggable to Elasticsearch later).

## Core Features

### Repository Hosting
- Create/fork/mirror repositories; support for bare repo storage with push-to-create disabled by default.
- Push/pull over SSH (deploy keys + personal keys) and HTTPS (token-based auth).
- Branch protection rules (require PR, require status checks, require N approvals, restrict force-push).
- Web-based file browser, blame, and commit history rendered from `git cat-file`/`git log` via a Go git library (go-git or shelling out to `git` for perf-critical paths).
- Large file support via Git LFS-compatible batch API in v1.1 (stubbed interface in v1).

### Authentication & Permissions
- Auth methods: username/password (bcrypt), SSH keys, personal access tokens (PATs) with scoped permissions, and OAuth2/OIDC for SSO (v1: generic OIDC provider support).
- Authorization model: Organization → Team → Repository, with roles `read`, `triage`, `write`, `maintain`, `admin`, mirroring GitHub's model for familiarity.
- Repo visibility: `private`, `internal` (visible to all authenticated users), `public`.
- All permission checks centralized in a single `authz` package invoked by both API handlers and the git daemon (no duplicated logic between HTTP and SSH paths).

### Pull Requests
- Fork-based and branch-based PRs within the same repo.
- Diff view computed via `git diff --numstat` + `git diff` per-file, cached in Redis keyed by `(base_sha, head_sha)`.
- Inline comments anchored to `(file_path, side, line)`, resilient to force-pushes via a best-effort line-remapping using the previous diff.
- Merge strategies: merge commit, squash, rebase. Merge executed server-side by the git daemon to keep git plumbing in one place.
- Required status checks via a generic "check run" API so external CI systems can report status.

### Issues
- Title, markdown body, labels, assignees, milestones.
- Cross-linking: `Fixes #123` in PR descriptions auto-closes issues on merge (parsed server-side, stored as an explicit `issue_links` table rather than regex-on-read).
- Comments with reactions; activity timeline (label changes, assignment, linked PR) stored as an append-only `events` table per issue.

## API Design

REST + JSON, versioned via URL prefix (`/api/v1/...`), modeled closely on GitHub's REST API to ease client/tooling migration.

- Auth: `Authorization: Bearer <PAT or OAuth token>`.
- Pagination: cursor-based (`?page_token=`), not offset-based, to stay stable under concurrent writes.
- Key resources: `/repos/{owner}/{repo}`, `/repos/{owner}/{repo}/pulls`, `/repos/{owner}/{repo}/pulls/{n}/reviews`, `/repos/{owner}/{repo}/issues`, `/orgs/{org}/teams`.
- Webhooks: per-repo and per-org, HMAC-signed payloads, at-least-once delivery with exponential backoff (5 retries via the worker queue), delivery log visible in UI for debugging.
- Rate limiting: token-bucket per-token, `X-RateLimit-*` headers, enforced at the API gateway layer via Redis.
- GraphQL is explicitly deferred post-v1 pending demand.

## Data Model

Core Postgres tables (simplified):

- `users(id, username, email, password_hash, created_at)`
- `orgs(id, name)`, `teams(id, org_id, name)`, `team_memberships(team_id, user_id, role)`
- `repositories(id, owner_type, owner_id, name, visibility, storage_shard, default_branch)`
- `repo_permissions(repo_id, subject_type, subject_id, role)` — subject is a user or team
- `pull_requests(id, repo_id, number, base_ref, head_ref, base_sha, head_sha, state, author_id)`
- `reviews(id, pr_id, reviewer_id, state, submitted_at)`
- `comments(id, target_type, target_id, author_id, body, line_anchor jsonb)`
- `issues(id, repo_id, number, title, body, state, author_id)`
- `issue_events(id, issue_id, type, actor_id, payload jsonb, created_at)`
- `webhooks(id, target_type, target_id, url, secret, events text[])`

Git object data lives entirely outside Postgres, on the repo storage layer; Postgres holds only metadata and pointers (SHAs), never blobs. This keeps the database small and backups fast — repo storage and Postgres are backed up independently.

## Non-Functional Requirements

- **Availability**: 99.9% target for single-region deployments; API and web servers are stateless and horizontally scalable, git daemon scales similarly given shared storage.
- **Performance**: p95 API latency < 200ms for metadata endpoints; clone/fetch throughput bound by storage I/O, target parity with native `git-daemon`.
- **Security**: all traffic TLS-only in production configs; secrets (webhook signing keys, OAuth client secrets) stored via env-injected secrets manager, never in Postgres in plaintext; audit log for auth changes, merges, force-pushes, and permission grants, retained 1 year.
- **Backup/DR**: nightly Postgres logical backups + continuous WAL archiving; repo storage snapshotted independently; documented RPO of 15 minutes, RTO of 4 hours for v1.
- **Observability**: structured logs (JSON), Prometheus metrics for request latency/queue depth/git operation counts, OpenTelemetry tracing across API → git daemon → storage.
- **Upgrade path**: schema migrations via versioned SQL files applied automatically on startup with a `--migrate-only` dry-run mode; zero-downtime rolling upgrades for API/web tier.
