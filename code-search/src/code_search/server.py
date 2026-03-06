"""FastMCP stdio server with load_code and prior_art_search tools."""

import os
from pathlib import Path

from mcp.server.fastmcp import FastMCP

from code_search.chunker import chunk_file, is_indexable
from code_search.embedder import Embedder
from code_search.search import cosine_similarity_search, format_results
from code_search.store import CodeSearchStore

mcp = FastMCP("code-search")

_embedder: Embedder | None = None
_store: CodeSearchStore | None = None


def _get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = Embedder()
    return _embedder


def _get_store() -> CodeSearchStore:
    global _store
    if _store is None:
        _store = CodeSearchStore()
    return _store


def _resolve_files(paths: list[str]) -> list[str]:
    """Resolve paths/directories into a flat list of indexable files."""
    files = []
    for p in paths:
        path = Path(p).expanduser().resolve()
        if path.is_file():
            if is_indexable(str(path)):
                files.append(str(path))
        elif path.is_dir():
            for child in sorted(path.rglob("*")):
                if child.is_file() and is_indexable(str(child)):
                    # Skip hidden dirs and common non-code dirs
                    parts = child.relative_to(path).parts
                    if any(
                        part.startswith(".")
                        or part in ("node_modules", "__pycache__", ".venv", "venv", "dist", "build")
                        for part in parts
                    ):
                        continue
                    files.append(str(child))
    return files


@mcp.tool()
async def load_code(paths: list[str], generate_descriptions: bool = False) -> str:
    """Index code files for semantic search.

    Resolves files from paths/directories, chunks them using tree-sitter
    (Python, JS, TS, Bash) or line-based fallback, embeds with
    nomic-embed-text-v1.5, and stores in SQLite.

    Args:
        paths: List of file or directory paths to index
        generate_descriptions: If True, generate Haiku descriptions for each chunk (requires API key)
    """
    store = _get_store()
    embedder = _get_embedder()

    files = _resolve_files(paths)
    if not files:
        return "No indexable files found in the provided paths."

    total_chunks = 0
    files_indexed = 0
    files_skipped = 0

    for file_path in files:
        try:
            current_mtime = os.path.getmtime(file_path)
        except OSError:
            continue

        stored_mtime = store.get_file_mtime(file_path)
        if stored_mtime is not None and stored_mtime >= current_mtime:
            files_skipped += 1
            continue

        # Re-index: delete old chunks, create new ones
        store.delete_file_chunks(file_path)

        chunks = chunk_file(file_path)
        if not chunks:
            continue

        # Batch embed all chunks for this file
        texts = [c.source_code for c in chunks]
        embeddings = embedder.embed_documents(texts)

        # Optionally generate descriptions
        descriptions: list[str | None] = [None] * len(chunks)
        if generate_descriptions:
            try:
                from code_search.describer import describe_chunks
                descriptions = await describe_chunks(chunks, file_path)
            except Exception:
                pass  # Graceful failure, chunks still indexed without descriptions

        for chunk, embedding, description in zip(chunks, embeddings, descriptions):
            store.insert_chunk(
                file_path=file_path,
                file_mtime=current_mtime,
                chunk_type=chunk.chunk_type,
                chunk_name=chunk.chunk_name,
                start_line=chunk.start_line,
                end_line=chunk.end_line,
                source_code=chunk.source_code,
                embedding=embedding,
                description=description,
            )

        total_chunks += len(chunks)
        files_indexed += 1

    stats = store.get_stats()
    return (
        f"Indexed {total_chunks} chunks from {files_indexed} files "
        f"({files_skipped} skipped, unchanged). "
        f"Total index: {stats['total_chunks']} chunks across {stats['total_files']} files."
    )


@mcp.tool()
async def prior_art_search(query: str, limit: int = 10) -> str:
    """Search indexed code by semantic similarity.

    Finds code chunks that are semantically similar to the query,
    useful for finding prior art, patterns, and relevant implementations.

    Args:
        query: Natural language description of what you're looking for
        limit: Maximum number of results to return (default 10)
    """
    store = _get_store()
    embedder = _get_embedder()

    chunks = store.get_all_chunks()
    if not chunks:
        return "No code indexed yet. Use load_code first to index some files."

    query_embedding = embedder.embed_query(query)
    results = cosine_similarity_search(query_embedding, chunks, limit=limit)

    return format_results(results)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
