#!/usr/bin/env bun
/**
 * FIFO pipe channel for Claude Code.
 *
 * Two-way channel using named pipes (mkfifo). Write to the inbound pipe
 * to send messages to Claude; read from the outbound pipe to receive replies.
 *
 * Pipes are created at:
 *   ~/.claude/channels/fifo-pipe/inbound.fifo
 *   ~/.claude/channels/fifo-pipe/outbound.fifo
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js'
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js'
import {
  ListToolsRequestSchema,
  CallToolRequestSchema,
} from '@modelcontextprotocol/sdk/types.js'
import { mkdirSync, existsSync, statSync } from 'fs'
import { homedir } from 'os'
import { join } from 'path'
import { execSync } from 'child_process'

const PIPE_DIR = process.env.FIFO_PIPE_DIR ?? join(homedir(), '.claude', 'channels', 'fifo-pipe')
const INBOUND_PIPE = join(PIPE_DIR, 'inbound.fifo')
const OUTBOUND_PIPE = join(PIPE_DIR, 'outbound.fifo')

function ensureFifo(path: string): void {
  if (existsSync(path)) {
    try {
      const st = statSync(path)
      if (st.isFIFO()) return
      // Not a FIFO — remove and recreate
      execSync(`rm -f ${JSON.stringify(path)}`)
    } catch {
      execSync(`rm -f ${JSON.stringify(path)}`)
    }
  }
  execSync(`mkfifo ${JSON.stringify(path)}`)
}

function ensurePipes(): void {
  mkdirSync(PIPE_DIR, { recursive: true })
  ensureFifo(INBOUND_PIPE)
  ensureFifo(OUTBOUND_PIPE)
}

ensurePipes()

let msgSeq = 0
function nextId(): string {
  return `fifo-${Date.now()}-${++msgSeq}`
}

// --- MCP Server ---

const mcp = new Server(
  { name: 'fifo-pipe', version: '0.1.0' },
  {
    capabilities: {
      experimental: { 'claude/channel': {} },
      tools: {},
    },
    instructions: [
      'Messages from the fifo-pipe channel arrive as <channel source="fifo-pipe" chat_id="fifo" message_id="...">.',
      'The sender is communicating via a named pipe (FIFO) on the local filesystem.',
      'Reply with the reply tool. The reply will be written to the outbound pipe for the sender to read.',
      `Pipe paths: inbound=${INBOUND_PIPE}, outbound=${OUTBOUND_PIPE}`,
    ].join('\n'),
  },
)

// --- Reply tool ---

mcp.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'reply',
      description: 'Send a reply message through the outbound FIFO pipe.',
      inputSchema: {
        type: 'object',
        properties: {
          chat_id: { type: 'string', description: 'The conversation ID (pass through from inbound message)' },
          text: { type: 'string', description: 'The message text to send' },
        },
        required: ['chat_id', 'text'],
      },
    },
  ],
}))

mcp.setRequestHandler(CallToolRequestSchema, async (req) => {
  if (req.params.name === 'reply') {
    const { text } = req.params.arguments as { chat_id: string; text: string }
    try {
      await writeToOutbound(text)
      return { content: [{ type: 'text', text: 'sent' }] }
    } catch (err) {
      return {
        content: [{ type: 'text', text: `reply failed: ${err instanceof Error ? err.message : err}` }],
        isError: true,
      }
    }
  }
  throw new Error(`unknown tool: ${req.params.name}`)
})

await mcp.connect(new StdioServerTransport())

// --- Outbound: write replies to the outbound pipe ---

async function writeToOutbound(text: string): Promise<void> {
  // Open the FIFO for writing. This will block until a reader is connected,
  // so we use a timeout via Bun's file API.
  const file = Bun.file(OUTBOUND_PIPE)
  const writer = file.writer()
  writer.write(text + '\n')
  await writer.flush()
  writer.end()
}

// --- Inbound: read lines from the inbound pipe and deliver to Claude ---

async function readInboundLoop(): Promise<void> {
  while (true) {
    try {
      // Opening a FIFO for reading blocks until a writer connects.
      // We use Bun.file + stream to read line by line.
      const file = Bun.file(INBOUND_PIPE)
      const stream = file.stream()
      const reader = stream.getReader()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += new TextDecoder().decode(value)
        const lines = buffer.split('\n')
        // Keep the last incomplete line in the buffer
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          const trimmed = line.trim()
          if (trimmed.length === 0) continue
          const id = nextId()
          await mcp.notification({
            method: 'notifications/claude/channel',
            params: {
              content: trimmed,
              meta: {
                chat_id: 'fifo',
                message_id: id,
                user: 'pipe',
                ts: new Date().toISOString(),
              },
            },
          })
        }
      }

      // If there's remaining content in buffer after stream ends
      if (buffer.trim().length > 0) {
        const id = nextId()
        await mcp.notification({
          method: 'notifications/claude/channel',
          params: {
            content: buffer.trim(),
            meta: {
              chat_id: 'fifo',
              message_id: id,
              user: 'pipe',
              ts: new Date().toISOString(),
            },
          },
        })
      }
    } catch (err) {
      // Log errors to stderr (visible in Claude Code debug logs) and retry
      process.stderr.write(`fifo-pipe: inbound read error: ${err}\n`)
      await new Promise((r) => setTimeout(r, 500))
    }
  }
}

process.stderr.write(`fifo-pipe: ready\n`)
process.stderr.write(`fifo-pipe: inbound  = ${INBOUND_PIPE}\n`)
process.stderr.write(`fifo-pipe: outbound = ${OUTBOUND_PIPE}\n`)

readInboundLoop()
