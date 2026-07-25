# GitForge Technical Specification

## Overview

GitForge is a self-hosted, web-based Git hosting platform. It gives teams repository management, code review, and issue tracking. Teams use GitForge when they must run their own infrastructure instead of GitHub, GitLab, or Bitbucket. GitForge targets engineering organizations that have compliance, data-residency, or air-gapped deployment needs. GitForge offers a single-binary deployment model or a Docker Compose deployment model. This keeps operational overhead low.

This spec covers the v1 scope. The v1 scope includes repository hosting over HTTP(S) and SSH, authentication and permissions, pull requests, issues, and the public API. The v1 scope does not include CI/CD runners, wikis, package registries, and federation between GitForge instances.

## Goals

- **Self-hostable in under 30 minutes**: Install GitForge through Docker Compose. GitForge needs only a single Postgres dependency. The core functions need no external services.
- **Git-native compatibility**: GitForge works with the stock `git` CLI over SSH and HTTPS. You do not need a custom client.
- **Familiar UX** for engineers coming from GitHub: PRs, inline diff comments, issue linking, branch protection.
- **Horizontally scalable**: the read path (clones and fetches) is separate from the write path (pushes, API). This design lets a single instance grow from 10 to 10,000 repos.
- **Auditable**: GitForge logs every permission change, merge, and force-push.

Non-goals for v1: multi-region replication, built-in CI, marketplace and app ecosystem.

## Architecture

GitForge has four services behind a reverse proxy:

1. **Web/API server** (Go): a stateless HTTP service that serves the REST API. It renders the web UI with server-rendered pages and a React SPA for the PR and diff views. The service scales horizontally behind a load balancer.
2. **Git daemon**: handles `git-upload-pack` and `git-receive-pack` over SSH, through a custom SSH server that embeds `golang.org/x/crypto/ssh`. It also handles smart HTTP. It talks to a shared repository store.
3. **Repository storage**: bare repos on a shared filesystem (NFS or EFS) for small deployments. Larger deployments use per-shard local disk with a repo-to-shard mapping table. Postgres never stores Git objects.
4. **Postgres**: the system of record for users, orgs, permissions, PRs, issues, comments, and webhooks. GitForge uses Redis for job queues (webhook delivery and PR-diff pre-computation) and for session and rate-limit caching.

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

Background workers use the same binary with the `--mode=worker` flag. They consume a Redis-backed queue for async work: webhook delivery, merge-conflict pre-check, and search indexing. Search indexing uses Postgres full-text search at the start. It can use Elasticsearch later.

## Core Features

### Repository Hosting
- Make, fork, or mirror repositories. GitForge supports bare repo storage, and it disables push-to-create by default.
- Push and pull over SSH (deploy keys and personal keys) and over HTTPS (token-based auth).
- Branch protection rules can need a PR, need status checks, need N approvals, or restrict force-pushes.
- A web-based file browser shows blame and commit history. It renders this data from `git cat-file` and `git log` through a Go git library (go-git), or it shells out to `git` for paths that need high performance.
- Large file support comes through a Git LFS-compatible batch API in v1.1. Version v1 has only a stubbed interface for this.

### Authentication & Permissions
- Auth methods: username and password (bcrypt), SSH keys, and personal access tokens (PATs) with scoped permissions. GitForge also supports OAuth2/OIDC for SSO. In v1, GitForge supports a generic OIDC provider.
- Authorization model: Organization → Team → Repository, with roles `read`, `triage`, `write`, `maintain`, `admin`, mirroring GitHub's model for familiarity.
- Repo visibility: `private`, `internal` (visible to all authenticated users), `public`.
- A single `authz` package centralizes all permission checks. Both the API handlers and the git daemon invoke this package. This design avoids duplicated logic between the HTTP and SSH paths.

### Pull Requests
- Fork-based and branch-based PRs within the same repo.
- GitForge computes the diff view through `git diff --numstat` and a per-file `git diff`. It caches the diff in Redis, keyed by `(base_sha, head_sha)`.
- Inline comments anchor to `(file_path, side, line)`. The comments resist force-pushes through a best-effort line-remapping that uses the previous diff.
- Merge strategies: merge commit, squash, or rebase. The git daemon does the merge on the server side. This keeps the git plumbing in one place.
- Status checks: GitForge needs status checks through a generic "check run" API. This lets external CI systems report status.

### Issues
- Title, markdown body, labels, assignees, milestones.
- When you write `Fixes #123` in a PR description, GitForge auto-closes the issue on merge. GitForge parses this server-side and stores it as an explicit `issue_links` table, instead of using regex-on-read.
- Comments support reactions. GitForge stores the activity timeline (label changes, assignment, linked PR) as an append-only `events` table per issue.

## API Design

The API uses REST and JSON. GitForge versions the API through a URL prefix (`/api/v1/...`). The API design follows GitHub's REST API closely, to make client and tooling migration easy.

- Auth: `Authorization: Bearer <PAT or OAuth token>`.
- Pagination: cursor-based (`?page_token=`), not offset-based, to stay stable under concurrent writes.
- Key resources: `/repos/{owner}/{repo}`, `/repos/{owner}/{repo}/pulls`, `/repos/{owner}/{repo}/pulls/{n}/reviews`, `/repos/{owner}/{repo}/issues`, `/orgs/{org}/teams`.
- Webhooks: GitForge sends webhooks per-repo and per-org, with HMAC-signed payloads. Delivery is at-least-once, with exponential backoff (5 retries through the worker queue). The delivery log is visible in the UI, for debugging.
- Rate limiting: GitForge uses a token-bucket per token, with `X-RateLimit-*` headers. The API gateway layer enforces rate limits through Redis.
- GitForge defers GraphQL until after v1, pending demand.

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

Git object data lives entirely outside Postgres, on the repo storage layer. Postgres holds only metadata and pointers (SHAs), and never holds blobs. This design keeps the database small and the backups fast. The team backs up repo storage and Postgres independently.

## Non-Functional Requirements

- **Availability**: the target is 99.9% for single-region deployments. The API and web servers are stateless and horizontally scalable. The git daemon scales in the same way, given shared storage.
- **Performance**: the p95 API latency target is under 200ms for metadata endpoints. Storage I/O bounds the clone and fetch throughput. The target is parity with the native `git-daemon`.
- **Security**: in production configs, all traffic is TLS-only. GitForge stores secrets (webhook signing keys, OAuth client secrets) through an env-injected secrets manager. GitForge never stores secrets in Postgres in plaintext. The audit log covers auth changes, merges, force-pushes, and permission grants. The team keeps the audit log for 1 year.
- **Backup and DR**: GitForge makes nightly Postgres logical backups, and it archives WAL continuously. The team snapshots repo storage independently. The documented RPO is 15 minutes. The documented RTO is 4 hours for v1.
- **Observability**: GitForge produces structured logs (JSON). Prometheus metrics cover request latency, queue depth, and git operation counts. OpenTelemetry tracing covers the path from API, to git daemon, to storage.
- **Upgrade path**: GitForge applies schema migrations automatically on startup, through versioned SQL files. A `--migrate-only` flag gives a dry-run mode. The API and web tier support zero-downtime rolling upgrades.
