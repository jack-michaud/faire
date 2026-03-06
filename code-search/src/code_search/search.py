"""Cosine similarity search over stored chunks."""

import numpy as np

from code_search.store import StoredChunk


def cosine_similarity_search(
    query_embedding: np.ndarray,
    chunks: list[StoredChunk],
    limit: int = 10,
) -> list[tuple[StoredChunk, float]]:
    """Search chunks by cosine similarity to query embedding."""
    if not chunks:
        return []

    # Stack all embeddings into a matrix
    embeddings = np.stack([c.embedding for c in chunks])

    # Normalize
    query_norm = query_embedding / (np.linalg.norm(query_embedding) + 1e-10)
    embed_norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-10
    normalized = embeddings / embed_norms

    # Cosine similarity = dot product of normalized vectors
    scores = normalized @ query_norm

    # Sort by score descending
    top_indices = np.argsort(scores)[::-1][:limit]

    return [(chunks[i], float(scores[i])) for i in top_indices]


def format_results(results: list[tuple[StoredChunk, float]]) -> str:
    """Format search results for display."""
    if not results:
        return "No results found."

    parts = []
    for chunk, score in results:
        header = f"**{chunk.file_path}** L{chunk.start_line}-{chunk.end_line} ({chunk.chunk_type}: {chunk.chunk_name}) [score: {score:.3f}]"
        desc = f"\n> {chunk.description}" if chunk.description else ""
        code = f"\n```\n{chunk.source_code}\n```"
        parts.append(f"{header}{desc}{code}")

    return "\n\n---\n\n".join(parts)
