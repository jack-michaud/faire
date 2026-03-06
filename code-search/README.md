# Code Search

Semantic code search MCP server for Claude Code. Indexes code into embeddings using [nomic-embed-text-v1.5](https://huggingface.co/nomic-ai/nomic-embed-text-v1.5) via ONNX, enabling "prior art" search that finds relevant patterns and implementations by meaning rather than keyword matching.

## Tools

### `load_code(paths, generate_descriptions?)`

Index code files for semantic search. Accepts file paths or directories (recursive). Uses tree-sitter for AST-aware chunking (Python, JS, TS, Bash) with line-based fallback for other file types. Incremental: skips files with unchanged mtime.

### `prior_art_search(query, limit?)`

Search indexed code by semantic similarity. Returns matching code chunks with file path, line range, source code, and similarity score.

## Installation

```bash
claude plugin install code-search@faire
```

## How It Works

1. **Chunking**: Tree-sitter extracts functions, classes, and methods from supported languages. Other files are split into overlapping line-based chunks.
2. **Embedding**: Chunks are embedded with nomic-embed-text-v1.5 (256-dim Matryoshka truncation) using fastembed (ONNX runtime, ~200MB).
3. **Storage**: Embeddings stored in per-project SQLite DB at `~/.claude/code-search/{hash}.db`.
4. **Search**: Cosine similarity between query embedding and stored chunk embeddings.

## Optional: Description Generation

Pass `generate_descriptions=True` to `load_code` to generate one-sentence Haiku descriptions for each chunk via the Agent SDK. Requires `ANTHROPIC_API_KEY`.
