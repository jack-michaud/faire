---
name: Create Claude Channel
description: Step-by-step procedure for building a Claude Code channel integration. Use when creating a new channel plugin that connects Claude Code to external systems via MCP, named pipes, webhooks, or chat platforms.
---

# Create a Claude Code Channel

## Overview

A Claude Code channel is an MCP server that pushes events into a Claude Code session so Claude can react to things happening outside the terminal. Channels can be one-way (alerts, webhooks) or two-way (chat bridges with reply tools).

This procedure walks through building, packaging, and testing a channel integration from scratch.

## Prerequisites

- Claude Code v2.1.80+ (`claude --version`)
- Bun, Node, or Deno runtime
- `@modelcontextprotocol/sdk` npm package
- A Claude Code plugin marketplace (or local project)

## Procedure

### Step 1: Create the project structure

Create a new plugin directory with the channel server and config files:

```
my-channel/
  package.json          # Dependencies
  server.ts             # MCP channel server
  plugin.json           # Plugin manifest
  .mcp.json             # MCP server config
```

Initialize the project:

```bash
mkdir my-channel && cd my-channel
bun init -y
bun add @modelcontextprotocol/sdk
```

### Step 2: Write the MCP channel server

The server has three essential parts:

1. **Server declaration** with `claude/channel` capability
2. **Stdio transport** connection (Claude Code spawns the server as a subprocess)
3. **Notification emitter** that pushes events into Claude's context

Minimal one-way server:

```typescript
#!/usr/bin/env bun
import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'

const mcp = new Server(
  { name: 'my-channel', version: '0.1.0' },
  {
    // claude/channel capability is REQUIRED — this registers the notification listener
    capabilities: { experimental: { 'claude/channel': {} } },
    // Instructions go into Claude's system prompt
    instructions: 'Events arrive as <channel source="my-channel" ...>. Act on them.',
  },
)

await mcp.connect(new StdioServerTransport())

// Push events to Claude:
await mcp.notification({
  method: 'notifications/claude/channel',
  params: {
    content: 'The event body text',
    meta: { key: 'value' },  // Each key becomes a <channel> tag attribute
  },
})
```

### Step 3: Add a reply tool (for two-way channels)

If Claude needs to send messages back, expose an MCP tool:

```typescript
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from '@modelcontextprotocol/sdk/types.js'

// Add tools capability to the Server constructor:
// capabilities: { experimental: { 'claude/channel': {} }, tools: {} }

mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [{
    name: 'reply',
    description: 'Send a reply back through this channel',
    inputSchema: {
      type: 'object',
      properties: {
        chat_id: { type: 'string', description: 'Conversation to reply in' },
        text: { type: 'string', description: 'Message to send' },
      },
      required: ['chat_id', 'text'],
    },
  }],
}))

mcp.setRequestHandler(CallToolRequestSchema, async (req) => {
  if (req.params.name === 'reply') {
    const { chat_id, text } = req.params.arguments as { chat_id: string; text: string }
    // Send the reply through your transport (pipe, HTTP, chat API, etc.)
    await sendReply(chat_id, text)
    return { content: [{ type: 'text', text: 'sent' }] }
  }
  throw new Error(`unknown tool: ${req.params.name}`)
})
```

Update instructions to tell Claude about the reply tool:

```typescript
instructions: 'Messages arrive as <channel source="my-channel" chat_id="...">. Reply with the reply tool, passing the chat_id from the tag.'
```

### Step 4: Implement the transport layer

Choose your transport based on the use case:

| Transport | Use Case | Example |
|-----------|----------|---------|
| Named pipes (mkfifo) | Local IPC between processes | fifo-pipe-channel |
| HTTP server | Webhooks, CI alerts | webhook-channel |
| Platform API polling | Chat platforms (Telegram, Discord) | telegram-channel |
| WebSocket | Real-time bidirectional | custom chat bridges |

For named pipes (see `resources/fifo-pipe-example.md` for full implementation):

```typescript
import { execSync } from 'child_process'

// Create pipes
execSync('mkfifo /path/to/inbound.fifo')
execSync('mkfifo /path/to/outbound.fifo')

// Read loop: watch inbound pipe, push to Claude
async function readLoop() {
  while (true) {
    const file = Bun.file('/path/to/inbound.fifo')
    const stream = file.stream()
    const reader = stream.getReader()
    // Read lines and call mcp.notification() for each
  }
}
```

For HTTP (webhooks):

```typescript
Bun.serve({
  port: 8788,
  hostname: '127.0.0.1',
  async fetch(req) {
    const body = await req.text()
    await mcp.notification({
      method: 'notifications/claude/channel',
      params: { content: body, meta: { path: new URL(req.url).pathname } },
    })
    return new Response('ok')
  },
})
```

### Step 5: Create plugin packaging files

**plugin.json:**

```json
{
  "name": "my-channel",
  "version": "0.1.0",
  "description": "Description of what this channel does",
  "author": { "name": "Your Name" },
  "mcpServers": "./.mcp.json"
}
```

**.mcp.json:**

```json
{
  "mcpServers": {
    "my-channel": {
      "command": "bun",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server.ts"]
    }
  }
}
```

**package.json:**

```json
{
  "name": "claude-channel-my-channel",
  "version": "0.1.0",
  "type": "module",
  "bin": "./server.ts",
  "scripts": { "start": "bun install --no-summary && bun server.ts" },
  "dependencies": { "@modelcontextprotocol/sdk": "^1.0.0" }
}
```

### Step 6: Register in marketplace (if applicable)

Add an entry to `.claude-plugin/marketplace.json`:

```json
{
  "name": "my-channel",
  "source": "./my-channel",
  "description": "...",
  "version": "0.1.0",
  "category": "communication"
}
```

### Step 7: Install and test

```bash
# Install the plugin
claude plugin install my-channel@your-marketplace

# Start Claude with the development channel flag
claude --dangerously-load-development-channels plugin:my-channel@your-marketplace

# Select "I am using this for local development" when prompted
```

Test the inbound path by sending data through your transport. Verify:
- Claude receives the message (shown as `← my-channel · ...` in the session)
- Claude uses the reply tool (if two-way)
- The reply reaches the other end of the transport

### Step 8: Security considerations

- **Gate inbound messages**: Check sender identity before calling `mcp.notification()` to prevent prompt injection
- **Localhost only**: Bind HTTP servers to `127.0.0.1`, not `0.0.0.0`
- **Permission relay** (optional): Declare `claude/channel/permission` capability to forward tool approval prompts remotely. Only do this if your channel authenticates the sender.

## Key Concepts

### Notification format

Events arrive in Claude's context as XML tags:

```
<channel source="my-channel" key1="val1" key2="val2">
The event body content
</channel>
```

- `source` is set automatically from the server name
- `meta` keys become tag attributes (letters, digits, underscores only)
- `content` becomes the tag body

### Instructions string

The `instructions` field in the Server constructor is injected into Claude's system prompt. It should tell Claude:
- What events to expect
- Whether to reply (and which tool to use)
- How to route replies (e.g., pass `chat_id` from the inbound tag)

### Development flag

Custom channels need `--dangerously-load-development-channels` during the research preview. Format: `plugin:<name>@<marketplace>` or `server:<name>` for bare MCP servers.

## Reference implementations

- **fakechat**: Web UI chat bridge — `external_plugins/fakechat` in claude-plugins-official
- **fifo-pipe-channel**: Named pipe transport — `fifo-pipe-channel/` in this repo
- **webhook example**: HTTP POST receiver — documented in channels reference docs
