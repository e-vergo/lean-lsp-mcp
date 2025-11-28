<h1 align="center">
  Lean LSP MCP
</h1>

<h3 align="center">Model Context Protocol Server for Lean 4 Theorem Proving</h3>

<p align="center">
  <a href="https://pypi.org/project/lean-lsp-mcp/">
    <img src="https://img.shields.io/pypi/v/lean-lsp-mcp.svg" alt="PyPI version" />
  </a>
  <a href="https://github.com/e-vergo/lean-lsp-mcp/blob/master/LICENSE">
    <img src="https://img.shields.io/github/license/e-vergo/lean-lsp-mcp.svg" alt="license" />
  </a>
</p>

An MCP server for agentic interaction with the [Lean theorem prover](https://lean-lang.org/) via the [Language Server Protocol](https://microsoft.github.io/language-server-protocol/specifications/lsp/3.17/specification/). This server provides comprehensive tools for LLM agents to understand, analyze, lint, and interact with Lean 4 projects.

## Features

* **Rich Lean Interaction**: Access diagnostics, goal states, term information, hover documentation, and code completions.
* **External Search Tools**: Integrated with LeanSearch, Loogle, Lean Finder, Lean Hammer, and State Search.
* **Auto-Linting (LAL)**: Automated code fixes for style violations, sorry reporting, dependency analysis, and axiom tracking.
* **Local Search**: Fast declaration lookup using ripgrep to prevent API hallucination.

## Quick Start

### Prerequisites

1. Install [uv](https://docs.astral.sh/uv/getting-started/installation/) (Python package manager)
2. Run `lake build` in your Lean project (ensures fast startup)
3. (Recommended) Install [ripgrep](https://github.com/BurntSushi/ripgrep) for local search

### Installation

<details>
<summary><b>VSCode</b></summary>

One-click install:

[![Install in VS Code](https://img.shields.io/badge/VS_Code-Install_Server-0098FF?style=flat-square&logo=visualstudiocode&logoColor=white)](https://insiders.vscode.dev/redirect/mcp/install?name=lean-lsp&config=%7B%22command%22%3A%22uvx%22%2C%22args%22%3A%5B%22lean-lsp-mcp%22%5D%7D)

Or manually add to `mcp.json` (Ctrl+Shift+P > "MCP: Open User Configuration"):

```jsonc
{
    "servers": {
        "lean-lsp": {
            "type": "stdio",
            "command": "uvx",
            "args": ["lean-lsp-mcp"]
        }
    }
}
```
</details>

<details>
<summary><b>Cursor</b></summary>

File > Preferences > Cursor Settings > MCP > "+ Add new global MCP Server":

```jsonc
{
    "mcpServers": {
        "lean-lsp": {
            "command": "uvx",
            "args": ["lean-lsp-mcp"]
        }
    }
}
```
</details>

<details>
<summary><b>Claude Code</b></summary>

```bash
# Local scope
claude mcp add lean-lsp uvx lean-lsp-mcp

# Project scope (creates .mcp.json)
claude mcp add lean-lsp -s project uvx lean-lsp-mcp
```
</details>

---

## Tool Reference

### LSP File Tools

#### `lean_file_outline`

Get a concise outline showing imports and declarations with type signatures.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Absolute path to Lean file |

**Returns**: Markdown-formatted outline with imports, theorems, definitions, classes, and structures.

---

#### `lean_file_contents`

> **DEPRECATED**: Will be removed. Use the Read tool or `lean_file_outline` instead.

Get the text contents of a Lean file with optional line numbers.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Absolute path to Lean file |
| `annotate_lines` | boolean | No | `true` | Annotate lines with line numbers |

---

#### `lean_diagnostic_messages`

Get all diagnostic messages (errors, warnings, infos) for a Lean file.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Absolute path to Lean file |
| `start_line` | integer | No | - | Filter from this line (1-indexed) |
| `end_line` | integer | No | - | Filter to this line (1-indexed) |
| `declaration_name` | string | No | - | Filter to specific declaration (overrides line filters) |

**Returns**: List of diagnostics with location, severity, and message.

<details>
<summary>Example output</summary>

```
l20c42-l20c46, severity: 1
simp made no progress

l21c11-l21c45, severity: 1
function expected at
  h_empty
term has type
  T ∩ compl T = ∅
```
</details>

---

#### `lean_goal`

Get the proof goals (tactic state) at a specific location.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Absolute path to Lean file |
| `line` | integer | Yes | - | Line number (1-indexed) |
| `column` | integer | No | - | Column number (1-indexed). If omitted, shows before and after |

**Returns**: Goal state or "no goals" if solved. To see goals at `sorry`, position cursor before the "s".

<details>
<summary>Example output</summary>

```
Before:
S : Type u_1
inst : Fintype S
P : Finset (Set S)
hPP : ∀ T ∈ P, ∀ U ∈ P, T ∩ U ≠ ∅
⊢ P.card = 2 ^ (Fintype.card S - 1)

After:
no goals
```
</details>

---

#### `lean_term_goal`

Get the expected type (term goal) at a specific position.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Absolute path to Lean file |
| `line` | integer | Yes | - | Line number (1-indexed) |
| `column` | integer | No | - | Column number (1-indexed). Defaults to end of line |

---

#### `lean_hover_info`

Get hover documentation for syntax, variables, functions, etc.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Absolute path to Lean file |
| `line` | integer | Yes | Line number (1-indexed) |
| `column` | integer | Yes | Column number (1-indexed). Use start of term |

<details>
<summary>Example output (hovering on `sorry`)</summary>

```
The `sorry` tactic is a temporary placeholder for an incomplete tactic proof,
closing the main goal using `exact sorry`.

This is intended for stubbing-out incomplete parts of a proof while still
having a syntactically correct proof skeleton. Lean will give a warning
whenever a proof uses `sorry`.
```
</details>

---

#### `lean_declaration_file`

Get the file contents where a symbol is declared.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Absolute path to Lean file containing the symbol reference |
| `symbol` | string | Yes | Symbol name to look up (case-sensitive) |

**Note**: The symbol must be present/imported in the file. Use `lean_hover_info` first to verify.

---

#### `lean_completions`

Get code completions at a location (for incomplete statements only).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Absolute path to Lean file |
| `line` | integer | Yes | - | Line number (1-indexed) |
| `column` | integer | Yes | - | Column number (1-indexed) |
| `max_completions` | integer | No | 32 | Maximum completions to return |

**Use cases**:
- **Dot completion**: After `Nat.` or `x.`
- **Identifier completion**: After partial name like `Nat.ad`
- **Import completion**: After `import` at file start

---

#### `lean_run_code`

Run a complete, self-contained Lean code snippet.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `code` | string | Yes | Complete Lean code (must include all imports) |

**Returns**: Diagnostics from compilation.

<details>
<summary>Example</summary>

Input: `#eval 5 * 7 + 3`

Output:
```
l1c1-l1c6, severity: 3
38
```
</details>

---

#### `lean_multi_attempt`

Try multiple code snippets at a line and compare results.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Absolute path to Lean file |
| `line` | integer | Yes | Line number (1-indexed) |
| `snippets` | array[string] | Yes | List of snippets to try (3+ recommended) |

**Note**: Single-line, fully-indented snippets only. Avoid comments.

<details>
<summary>Example output</summary>

```
  rw [Nat.pow_sub (Fintype.card_pos)]:
⊢ P.card = 2 ^ (Fintype.card S - 1)
l14c7-l14c51, severity: 1
unknown constant 'Nat.pow_sub'

  by_contra h_neq:
h_neq : ¬P.card = 2 ^ (Fintype.card S - 1)
⊢ False
```
</details>

---

### Local Search

#### `lean_local_search`

Search for declarations in the workspace to prevent hallucinating APIs.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Declaration name or prefix |
| `limit` | integer | No | 10 | Maximum matches to return |
| `project_root` | string | No | - | Project root path |

**Returns**: List of `{name, kind, file}` objects.

**Requires**: [ripgrep](https://github.com/BurntSushi/ripgrep) installed.

---

### External Search Tools

> **Rate Limit**: Most external tools are limited to 3 requests per 30 seconds.

#### `lean_leansearch`

Search Mathlib using natural language via [leansearch.net](https://leansearch.net).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query (see patterns below) |
| `num_results` | integer | No | 5 | Maximum results |

**Query patterns**:
- Natural language: `"If there exist injective maps from A to B and B to A, then there exists a bijective map"`
- Mixed: `"n + 1 <= m if n < m"`
- Concept: `"Cauchy Schwarz"`
- Identifier: `"List.sum"`, `"Finset induction"`
- Lean term: `"{f : A → B} (hf : Injective f) : ∃ h, Bijective h"`

**Citation**: [arXiv:2403.13310](https://arxiv.org/abs/2403.13310)

---

#### `lean_loogle`

Search by type signature via [loogle.lean-lang.org](https://loogle.lean-lang.org/).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Search query (see patterns below) |
| `num_results` | integer | No | 8 | Maximum results |

**Query patterns**:
- By constant: `Real.sin`
- By name substring: `"differ"`
- By subexpression: `_ * (_ ^ _)`
- Non-linear: `Real.sqrt ?a * Real.sqrt ?a`
- By type: `(?a -> ?b) -> List ?a -> List ?b`
- By conclusion: `|- tsum _ = _ * tsum _`

**Repository**: [github.com/nomeata/loogle](https://github.com/nomeata/loogle)

---

#### `lean_leanfinder`

Semantic search via [Lean Finder](https://huggingface.co/spaces/delta-lab-ai/Lean-Finder).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `query` | string | Yes | - | Mathematical concept, proof state, or statement |
| `num_results` | integer | No | 5 | Maximum results |

**Effective queries**:
- Natural language statement: `"For any n,m, n+m = m+n"`
- Question: `"Does y being a root of minpoly(x) imply minpoly(x)=minpoly(y)?"`
- Proof state + transformation goal
- Statement fragment

**Citation**: [arXiv:2510.15940](https://arxiv.org/abs/2510.15940)

---

#### `lean_state_search`

Search for applicable theorems based on proof state via [premise-search.com](https://premise-search.com/).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Absolute path to Lean file |
| `line` | integer | Yes | - | Line number (1-indexed) |
| `column` | integer | Yes | - | Column number (1-indexed) |
| `num_results` | integer | No | 5 | Maximum results |

**Returns**: List of `{name, formal_type, module}` for relevant theorems.

**Self-hosting**: Set `LEAN_STATE_SEARCH_URL` environment variable.

**Citation**: [arXiv:2501.13959](https://arxiv.org/abs/2501.13959)

---

#### `lean_hammer_premise`

Search for premises using [Lean Hammer](https://github.com/hanwenzhu/lean-premise-server).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Absolute path to Lean file |
| `line` | integer | Yes | - | Line number (1-indexed) |
| `column` | integer | Yes | - | Column number (1-indexed) |
| `num_results` | integer | No | 32 | Maximum results |

**Returns**: List of premise names.

**Self-hosting**: Set `LEAN_HAMMER_URL` environment variable.

**Citation**: [arXiv:2506.07477](https://arxiv.org/abs/2506.07477)

---

### LAL Tools (Auto-Linting)

#### `lal_fix_diagnostics`

Auto-fix mechanical linter warnings.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Absolute path to file or directory |
| `dry_run` | boolean | No | `true` | Show fixes without applying |
| `recursive` | boolean | No | `false` | Process directories recursively |
| `glob_pattern` | string | No | - | Filter files (e.g., `"**/*.lean"`) |

**Supported fixes**:

| Violation | Fix |
|-----------|-----|
| Unused variables | `x` → `_x` |
| Wrong cdot | `.` → `·` |
| Lambda syntax | `λ` → `fun` |
| Dollar syntax | `$` → `<\|` |
| "Try this:" suggestions | Auto-apply |
| Unused simp args | Remove |
| Trailing whitespace | Remove |
| Windows line endings | Convert to Unix |
| Semicolon spacing | Fix |

<details>
<summary>Example output</summary>

```json
[
  {"file": "/path/file.lean", "line": 10, "column": 5, "replacement": "fun", "description": "Replace λ with fun keyword"},
  {"file": "/path/file.lean", "line": 15, "column": 8, "replacement": "_x", "description": "Prefix unused variable `x` with underscore"}
]
```
</details>

---

#### `lal_sorry_report`

Report `sorry` occurrences in Lean files.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Absolute path to file or directory |
| `verbose` | boolean | No | `false` | Include declaration and goal fields |
| `recursive` | boolean | No | `false` | Process directories recursively |
| `glob_pattern` | string | No | - | Filter files (e.g., `"**/*.lean"`) |

<details>
<summary>Example output</summary>

```json
{
  "file": "/path/to/file.lean",
  "sorry_count": 2,
  "sorry_locations": [
    {"line": 15, "column": 3},
    {"line": 42, "column": 5}
  ]
}
```
</details>

---

#### `lal_custom_deps`

Report custom (non-standard library) dependencies.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Absolute path to file or directory |
| `recursive` | boolean | No | `false` | Process directories recursively |
| `glob_pattern` | string | No | - | Filter files |

Identifies imports not from Mathlib, Batteries, Lean, or Init.

<details>
<summary>Example output</summary>

```json
{
  "file": "/path/to/file.lean",
  "custom_deps": ["MyProject.Helper", "MyProject.Types"],
  "custom_deps_detailed": [
    {"name": "MyProject.Helper", "line": 3},
    {"name": "MyProject.Types", "line": 4}
  ]
}
```
</details>

---

#### `lal_trivial_report`

Report trivial statements (rfl, trivial, by decide, etc.).

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Absolute path to file or directory |
| `recursive` | boolean | No | `false` | Process directories recursively |
| `glob_pattern` | string | No | - | Filter files |

Identifies statements using `rfl`, `trivial`, `by decide`, or `by simp` with no arguments.

---

#### `lal_file_context`

Get combined file context in a single call.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `file_path` | string | Yes | - | Absolute path to Lean file |
| `verbose` | boolean | No | `false` | Include full sorry details |
| `declaration` | string | No | - | Include axiom info for this declaration |

**Returns**: Aggregated sorry count, custom deps, and optional axiom info.

<details>
<summary>Example output</summary>

```json
{
  "file": "/path/to/file.lean",
  "sorry_count": 2,
  "sorry_locations": [{"line": 15, "column": 3}, {"line": 42, "column": 5}],
  "custom_deps": ["MyProject.Helper"],
  "custom_deps_detailed": [{"name": "MyProject.Helper", "line": 3}],
  "axioms": {
    "declaration": "my_theorem",
    "axioms": ["propext", "Classical.choice"],
    "count": 2
  }
}
```
</details>

---

### Analysis Tools

#### `lean_axiom_report`

Report axioms used by a declaration.

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `file_path` | string | Yes | Absolute path to Lean file |
| `declaration_name` | string | Yes | Declaration name (case-sensitive) |

**Returns**: `{declaration, axioms, count}` showing axiom dependencies.

<details>
<summary>Example output</summary>

```json
{
  "declaration": "my_theorem",
  "axioms": ["propext", "Classical.choice"],
  "count": 2
}
```
</details>

---

### Project Tools

#### `lean_build`

Rebuild the Lean project and restart the LSP server.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `lean_project_path` | string | No | - | Path to project (auto-detected if omitted) |
| `clean` | boolean | No | `false` | Run `lake clean` first (slow!) |

---

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LEAN_PROJECT_PATH` | Lean project root path | Auto-detected |
| `LEAN_LOG_LEVEL` | Log level: INFO, WARNING, ERROR, NONE | INFO |
| `LEAN_LSP_MCP_TOKEN` | Bearer token for HTTP transport | - |
| `LEAN_STATE_SEARCH_URL` | Self-hosted premise-search URL | https://premise-search.com |
| `LEAN_HAMMER_URL` | Self-hosted Lean Hammer URL | http://leanpremise.net |
| `LAL_PATH` | Path to LAL binary | Auto-detected |

### Transport Methods

```bash
uvx lean-lsp-mcp --transport stdio              # Default
uvx lean-lsp-mcp --transport streamable-http    # HTTP at :8000/mcp
uvx lean-lsp-mcp --transport sse --port 12345   # SSE at :12345/sse
```

### LAL Setup

For auto-linting features, [LAL](https://github.com/e-vergo/LAL) is auto-detected if installed as a sibling directory, or set `LAL_PATH`:

```bash
git clone https://github.com/e-vergo/LAL && cd LAL && lake build lal
export LAL_PATH=/path/to/LAL/.lake/build/bin/lal
```

---

## Security Notes

This MCP server is a research tool in beta. It has file system access and no input validation. Please audit the code and report security issues.

See [Awesome MCP Security](https://github.com/Puliczek/awesome-mcp-security) for general MCP security information.

---

## Development

```bash
# MCP Inspector
npx @modelcontextprotocol/inspector uvx --with-editable . python -m lean_lsp_mcp.server

# Run tests
uv sync --all-extras
uv run pytest tests
```

---

## Publications

- Ax-Prover: A Deep Reasoning Agentic Framework for Theorem Proving ([arXiv:2510.12787](https://arxiv.org/abs/2510.12787))

## Related Projects

- [LeanTool](https://github.com/GasStationManager/LeanTool)
- [LeanExplore MCP](https://www.leanexplore.com/docs/mcp)

---

## License & Credits

**MIT** licensed. See [LICENSE](LICENSE).

This project builds on [lean-lsp-mcp](https://github.com/oOo0oOo/lean-lsp-mcp) by Oliver Dressler and integrates [LAL (Lean Auto Linter)](https://github.com/e-vergo/LAL).

```bibtex
@software{lean-lsp-mcp,
  author = {Oliver Dressler},
  title = {{Lean LSP MCP: Tools for agentic interaction with the Lean theorem prover}},
  url = {https://github.com/oOo0oOo/lean-lsp-mcp},
  year = {2025}
}
```
