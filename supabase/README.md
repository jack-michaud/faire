# Supabase Plugin

A specialized Claude Code plugin for Supabase operations, providing an expert agent for database migrations, RLS policies, Edge Functions, and Realtime features.

## Features

The Supabase plugin includes a specialized agent that helps you:

- **Create Database Migrations** - Generate properly formatted migration files with best practices
- **Manage Declarative Schemas** - Use the declarative schema workflow with `supabase/schemas/`
- **Write RLS Policies** - Create secure, performant Row Level Security policies
- **Build Database Functions** - Create PostgreSQL functions following security best practices
- **Develop Edge Functions** - Write Deno-based Edge Functions with proper dependencies
- **Implement Realtime** - Set up broadcast channels, database triggers, and RLS authorization
- **Follow Style Guidelines** - Ensure all SQL follows the project's Postgres style guide

## Installation

1. Add the marketplace to Claude Code (if not already added):
   ```bash
   /plugin marketplace add /path/to/faire
   ```

2. Install the Supabase plugin:
   ```bash
   /plugin install supabase@faire
   ```

3. Restart Claude Code to load the plugin

## Usage

The plugin provides a `supabase-expert` agent that automatically activates when you work with Supabase-related tasks. You can also invoke it explicitly:

```
Use the supabase-expert agent to create a migration for a new users table
```

Or let Claude Code automatically dispatch it when working with Supabase:

```
Create a migration that adds a posts table with RLS policies
```

## Agent Capabilities

The `supabase-expert` agent has access to comprehensive resource files that define best practices:

### Database Operations
- Creating properly named migration files (YYYYMMDDHHmmss_description.sql)
- Using declarative schema workflow with `supabase/schemas/`
- Following Postgres style guide (lowercase SQL, snake_case, comments)

### Security
- Enabling RLS on all tables
- Creating granular policies (separate for SELECT, INSERT, UPDATE, DELETE)
- Using auth.uid() and auth.jwt() helper functions
- Optimizing policies with proper indexes

### Edge Functions
- Using Deno.serve for HTTP handlers
- Leveraging pre-populated environment variables
- Using npm: and jsr: specifiers for dependencies
- Following Deno and Web API best practices

### Realtime
- Preferring `broadcast` over `postgres_changes`
- Using dedicated topics (scope:entity pattern)
- Implementing private channels with RLS
- Creating database triggers with realtime.broadcast_changes

## Requirements

- Supabase CLI installed (`npm install -g supabase` or via package manager)
- Active Supabase project (local or remote)
- Claude Code with plugin support

## Examples

### Create a Migration
```
Create a migration for a comments table with user_id foreign key and RLS policies
```

The agent will:
1. Read the migration guidelines
2. Generate a properly named file in `supabase/migrations/`
3. Include proper SQL with comments
4. Enable RLS and create granular policies

### Create an Edge Function
```
Create an Edge Function that sends email notifications using Resend
```

The agent will:
1. Read the Edge Function guidelines
2. Create function in `supabase/functions/`
3. Use proper Deno imports and Web APIs
4. Leverage environment variables

### Implement Realtime
```
Set up Realtime broadcasts for the messages table using private channels
```

The agent will:
1. Read the Realtime guidelines
2. Create database trigger using realtime.broadcast_changes
3. Set up RLS policies on realtime.messages
4. Provide client-side subscription code

## Resource Files

The agent consults these resource files (located in `supabase/resources/`):

- `database-creating-database-migration.md` - Migration creation guidelines
- `database-declarative-database-schema.md` - Declarative schema workflow
- `database-create-rls-policies.md` - RLS policy best practices
- `database-create-functions.md` - Database function patterns
- `database-postgres-style-guide.md` - SQL style guidelines
- `writing-edge-functions.md` - Edge Function best practices
- `supabase-realtime.md` - Realtime implementation guide

## Troubleshooting

### Agent not activating
- Ensure the plugin is installed: `/plugin list`
- Check agent is available: `/agents`
- Explicitly invoke: "Use supabase-expert to..."

### CLI commands failing
- Verify Supabase CLI is installed: `supabase --version`
- Ensure you're in a Supabase project directory
- Check local Supabase is running: `supabase status`

### Migrations not applying
- Review the generated migration file for syntax errors
- Check migration naming format (YYYYMMDDHHmmss_description.sql)
- Ensure file is in `supabase/migrations/` directory

## Contributing

To improve the Supabase plugin:

1. Add or update resource files in `supabase/resources/`
2. Update the agent configuration in `supabase/agents/supabase-expert.md`
3. Test the changes with various Supabase operations
4. Update this README with new features or examples

## License

MIT
