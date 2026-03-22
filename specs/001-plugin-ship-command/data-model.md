# Data Model: Plugin Ship Command

**Date**: 2026-03-22

This feature operates on existing file-system entities. No new data entities are introduced.

## Existing Entities (referenced, not modified)

### Skill
- **Location**: `<plugin>/skills/<skill-name>/SKILL.md`
- **Format**: Markdown with YAML frontmatter
- **Required fields**: `name` (string), `description` (string, trigger condition)
- **Optional**: `resources/` subdirectory with supporting markdown files

### Command
- **Location**: `<plugin>/commands/<command-name>.md`
- **Format**: Markdown with YAML frontmatter
- **Required fields**: `description` (string)
- **Optional fields**: `allowed-tools` (comma-separated string), `argument-hint` (string)

### Plugin Manifest
- **Location**: `<plugin>/plugin.json`
- **Format**: JSON
- **Key fields**: `name`, `version` (semver string), `description`, `skills` (optional, path to skills dir)

### Marketplace Manifest
- **Location**: `.claude-plugin/marketplace.json`
- **Format**: JSON
- **Contains**: Array of plugin entries with `name`, `version`, `source`

## State Transitions

### Faire Ship Workflow
```
idle → fetch → workspace_created → content_written → validated → version_bumped → committed → pushed → workspace_cleaned → done
```

At any step, validation failure transitions to `aborted` with error report.

### Local Ship Workflow
```
idle → content_written → validated → committed → done
```

## Validation Rules

- SKILL.md: Must have YAML frontmatter with non-empty `name` and `description`
- Command .md: Must have YAML frontmatter with non-empty `description`
- plugin.json: Must be valid JSON; `version` must be incremented from previous value
- marketplace.json: Must be valid JSON; plugin entry version must match plugin.json
