<!--
Sync Impact Report
==================
Version change: 1.0.0 → 1.1.0
Modified principles:
  - II. Convention-Driven Components → expanded to explicitly serve
    coding agents as primary consumers of documentation and procedures
Added sections:
  - Mission statement (below title)
  - "Automate the Rote" subsection in Development Workflow
Removed sections: none
Templates requiring updates:
  - .specify/templates/plan-template.md ✅ no changes needed
  - .specify/templates/spec-template.md ✅ no changes needed
  - .specify/templates/tasks-template.md ✅ no changes needed
Follow-up TODOs: none
-->

# Faire Plugin Marketplace Constitution

**Mission**: Build a plugin marketplace whose plugins improve over
time through well-documented procedures that coding agents can
execute autonomously. Every skill, hook, and command doubles as
executable documentation — readable by humans, actionable by agents.

## Core Principles

### I. Plugin Independence

Each plugin in the marketplace MUST be independently versioned,
installable, and self-contained. A plugin MUST NOT depend on another
plugin at install time. Plugins MUST declare all their components
(skills, hooks, commands, agents, MCP servers) in their own
`plugin.json` manifest. Users MUST be able to install any single
plugin without installing the rest of the marketplace.

**Rationale**: The marketplace exists so users pick only what they
need. Coupling between plugins defeats this purpose and creates
upgrade friction.

### II. Convention-Driven Components

All plugin components MUST follow the established structural patterns:

- **Skills**: Markdown with YAML frontmatter (`name`, `description`);
  main content in `SKILL.md`. Procedures MUST be written as
  step-by-step instructions that a coding agent can follow without
  ambiguity.
- **Hooks**: Defined in `hooks/hooks.json`; scripts read JSON from
  stdin and write JSON to stdout.
- **Slash Commands**: Markdown with YAML frontmatter that expand to
  prompts.
- **Agents**: Markdown with system prompt; may reference a
  `resources/` directory.
- **MCP Servers**: Configured in the `mcpServers` array of
  `plugin.json`.

New component types MUST be documented in the plugin's README before
merging. Documentation MUST be written with coding agents as the
primary consumer — explicit, unambiguous, and executable. If an agent
cannot follow a procedure without human clarification, the procedure
is incomplete.

**Rationale**: Consistent, agent-readable patterns are how plugins
improve over time. Every procedure captured is a procedure that can
be executed autonomously across any project that installs the plugin.

### III. Simplicity First

Every change MUST be the minimum needed for the current task.
Prefer editing existing files over creating new ones. Prefer small,
focused files (200-400 lines typical, 800 max). Do not add
abstractions, configuration options, or error handling for scenarios
that cannot occur. When in doubt, leave it out.

**Rationale**: Plugin marketplaces grow fast. Unnecessary complexity
compounds across plugins and makes maintenance unsustainable.

## Plugin Architecture Constraints

- The marketplace manifest (`.claude-plugin/marketplace.json`) MUST
  list every plugin with accurate metadata and current version.
- Each plugin directory MUST contain a `plugin.json` and a `README.md`.
- Plugins MUST use semantic versioning (`MAJOR.MINOR.PATCH`).
- Patch version MUST be bumped on any content change (skill updates,
  hook fixes, doc tweaks) before pushing to main.
- Minor version MUST be bumped when adding new components (a new
  skill, command, agent, or hook).
- Major version MUST be bumped for breaking changes (renamed
  commands, removed skills, changed hook contracts).

## Development Workflow

- Use `jj` for version control operations.
- Small skill/procedure updates: bump patch, commit, push to main
  without waiting for explicit approval.
- Larger changes (new plugins, new component types, breaking changes):
  plan first, then implement.
- Test plugins locally before pushing:
  `claude plugin marketplace add <path>` then
  `claude plugin install <name>@faire`.
- Commit messages follow conventional format:
  `<type>: <description>` (feat, fix, refactor, docs, test, chore).

### Automate the Rote

Repetitive, error-prone operations MUST be scripted rather than
performed manually. If a task is done more than twice and has a
known-correct sequence, it MUST become a Makefile target, shell
script, or hook. Examples:

- **Version bumping**: `make bump-patch PLUGIN=<name>` — MUST be
  used instead of hand-editing version strings in `plugin.json` and
  `marketplace.json`.
- **Linting/formatting**: MUST be runnable via a single Makefile
  target (e.g., `make lint`).
- **Plugin validation**: Structure checks (plugin.json exists,
  README exists, versions in sync) SHOULD be scripted and runnable
  before push.

When adding a new rote task, prefer extending the existing Makefile
over creating standalone scripts. Scripts MUST be idempotent and
safe to re-run.

## Governance

This constitution is the authoritative source of project-level rules
for the Faire marketplace. All contributions MUST comply.

**Amendment procedure**:
1. Propose the change with rationale.
2. Update this file with the amendment.
3. Increment the version per semantic versioning:
   - MAJOR: principle removal or incompatible redefinition.
   - MINOR: new principle or materially expanded guidance.
   - PATCH: wording clarification, typo fix, non-semantic refinement.
4. Update `LAST_AMENDED_DATE` to the date of the change.
5. Propagate any downstream impact to templates and docs.

**Compliance review**: Any spec, plan, or task list produced by
speckit commands SHOULD be checked against this constitution before
finalization.

**Version**: 1.1.0 | **Ratified**: 2026-03-22 | **Last Amended**: 2026-03-22
