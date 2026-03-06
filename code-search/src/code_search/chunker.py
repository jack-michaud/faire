"""Tree-sitter AST parsing + fallback line-based chunking."""

from dataclasses import dataclass
from pathlib import Path

import tree_sitter_bash as ts_bash
import tree_sitter_javascript as ts_javascript
import tree_sitter_python as ts_python
import tree_sitter_typescript as ts_typescript
from tree_sitter import Language, Parser

PYTHON_LANG = Language(ts_python.language())
JS_LANG = Language(ts_javascript.language())
TS_LANG = Language(ts_typescript.language_typescript())
TSX_LANG = Language(ts_typescript.language_tsx())
BASH_LANG = Language(ts_bash.language())

EXTENSION_TO_LANGUAGE: dict[str, Language] = {
    ".py": PYTHON_LANG,
    ".js": JS_LANG,
    ".jsx": JS_LANG,
    ".ts": TS_LANG,
    ".tsx": TSX_LANG,
    ".sh": BASH_LANG,
    ".bash": BASH_LANG,
}

PYTHON_NODE_TYPES = {"function_definition", "class_definition"}
JS_NODE_TYPES = {
    "function_declaration",
    "class_declaration",
    "method_definition",
    "arrow_function",
}
BASH_NODE_TYPES = {"function_definition"}

LANGUAGE_NODE_TYPES: dict[Language, set[str]] = {
    PYTHON_LANG: PYTHON_NODE_TYPES,
    JS_LANG: JS_NODE_TYPES,
    TS_LANG: JS_NODE_TYPES,
    TSX_LANG: JS_NODE_TYPES,
    BASH_LANG: BASH_NODE_TYPES,
}

INDEXABLE_EXTENSIONS = {
    ".py", ".js", ".jsx", ".ts", ".tsx", ".sh", ".bash",
    ".md", ".txt", ".json", ".yaml", ".yml", ".toml",
    ".html", ".css", ".scss", ".sql", ".rs", ".go",
    ".java", ".rb", ".c", ".cpp", ".h", ".hpp",
}

FALLBACK_CHUNK_LINES = 50
FALLBACK_OVERLAP = 10


@dataclass(frozen=True)
class CodeChunk:
    chunk_type: str
    chunk_name: str
    start_line: int
    end_line: int
    source_code: str


def _get_chunk_name(node, source_lines: list[str]) -> str:
    """Extract a meaningful name from an AST node."""
    # Look for name child
    for child in node.children:
        if child.type == "identifier":
            return child.text.decode("utf-8")
        if child.type == "property_identifier":
            return child.text.decode("utf-8")

    # For arrow functions, check parent variable_declarator
    if node.type == "arrow_function" and node.parent:
        if node.parent.type == "variable_declarator":
            for child in node.parent.children:
                if child.type == "identifier":
                    return child.text.decode("utf-8")

    # Fallback: first line trimmed
    line = source_lines[node.start_point[0]].strip()
    return line[:60] if len(line) > 60 else line


def _get_chunk_type(node) -> str:
    """Map AST node type to chunk type."""
    type_map = {
        "function_definition": "function",
        "function_declaration": "function",
        "class_definition": "class",
        "class_declaration": "class",
        "method_definition": "method",
        "arrow_function": "function",
    }
    return type_map.get(node.type, "block")


def _walk_for_nodes(node, target_types: set[str]) -> list:
    """Walk AST and collect nodes of target types."""
    results = []
    if node.type in target_types:
        results.append(node)
        # For classes, also look for methods inside
        if node.type in ("class_definition", "class_declaration"):
            for child in node.children:
                if child.type == "class_body" or child.type == "block":
                    for grandchild in child.children:
                        if grandchild.type in ("method_definition", "function_definition"):
                            results.append(grandchild)
        return results

    for child in node.children:
        # For arrow functions, only collect if parent is variable_declarator
        if child.type == "arrow_function":
            if node.type == "variable_declarator":
                results.append(child)
        else:
            results.extend(_walk_for_nodes(child, target_types))

    return results


def _chunk_with_tree_sitter(source: str, language: Language) -> list[CodeChunk]:
    """Parse source with tree-sitter and extract semantic chunks."""
    parser = Parser(language)
    tree = parser.parse(source.encode("utf-8"))
    source_lines = source.split("\n")
    target_types = LANGUAGE_NODE_TYPES.get(language, set())

    nodes = _walk_for_nodes(tree.root_node, target_types)

    chunks = []
    for node in nodes:
        start_line = node.start_point[0] + 1  # 1-indexed
        end_line = node.end_point[0] + 1
        chunk_source = "\n".join(source_lines[start_line - 1 : end_line])
        chunks.append(
            CodeChunk(
                chunk_type=_get_chunk_type(node),
                chunk_name=_get_chunk_name(node, source_lines),
                start_line=start_line,
                end_line=end_line,
                source_code=chunk_source,
            )
        )

    return chunks


def _chunk_by_lines(source: str, file_path: str) -> list[CodeChunk]:
    """Fallback: split into overlapping line-based chunks."""
    lines = source.split("\n")
    total = len(lines)
    if total == 0:
        return []

    chunks = []
    start = 0
    chunk_idx = 0
    while start < total:
        end = min(start + FALLBACK_CHUNK_LINES, total)
        chunk_source = "\n".join(lines[start:end])
        if chunk_source.strip():
            chunks.append(
                CodeChunk(
                    chunk_type="text_block",
                    chunk_name=f"{Path(file_path).name}:{start + 1}-{end}",
                    start_line=start + 1,
                    end_line=end,
                    source_code=chunk_source,
                )
            )
        chunk_idx += 1
        start = end - FALLBACK_OVERLAP if end < total else total

    return chunks


def chunk_file(file_path: str) -> list[CodeChunk]:
    """Chunk a file using tree-sitter if supported, else line-based."""
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext not in INDEXABLE_EXTENSIONS:
        return []

    try:
        source = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, UnicodeDecodeError):
        return []

    if not source.strip():
        return []

    language = EXTENSION_TO_LANGUAGE.get(ext)
    if language:
        chunks = _chunk_with_tree_sitter(source, language)
        # If tree-sitter found nothing, fall back to line-based
        if not chunks:
            return _chunk_by_lines(source, file_path)
        return chunks

    return _chunk_by_lines(source, file_path)


def is_indexable(file_path: str) -> bool:
    """Check if a file should be indexed."""
    return Path(file_path).suffix.lower() in INDEXABLE_EXTENSIONS
