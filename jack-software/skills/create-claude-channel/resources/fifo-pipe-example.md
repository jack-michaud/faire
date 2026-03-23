# FIFO Pipe Channel — Complete Implementation

A two-way channel using named pipes (`mkfifo`) for local inter-process communication.

## How It Works

Two named pipes are created:
- **inbound.fifo**: External process writes messages here → Claude reads them
- **outbound.fifo**: Claude writes replies here → External process reads them

The MCP server continuously reads from the inbound pipe in a loop. When a line arrives, it pushes a `notifications/claude/channel` event to Claude. When Claude calls the `reply` tool, the server writes to the outbound pipe.

## Usage

From a terminal, send a message and read the reply:

```bash
# Start a reader for the reply in the background
cat ~/.claude/channels/fifo-pipe/outbound.fifo > /tmp/reply.txt &

# Send a message
echo "Hello, what is 2+2?" > ~/.claude/channels/fifo-pipe/inbound.fifo

# Wait and read the reply
sleep 10
cat /tmp/reply.txt
```

## Key Implementation Details

- `Bun.file(path).stream()` opens a FIFO for reading and returns a ReadableStream
- The read loop re-opens the pipe after each EOF (writer disconnects), enabling repeated messages
- `Bun.file(path).writer()` opens for writing; flush and end after each reply
- Pipes are created at startup with `mkfifo` via `execSync`
- The server checks `statSync(path).isFIFO()` to avoid overwriting regular files

## Full Server Source

See `fifo-pipe-channel/server.ts` in the repo root for the complete implementation.
