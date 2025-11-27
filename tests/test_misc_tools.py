from __future__ import annotations

import textwrap
from collections.abc import Callable
from pathlib import Path
from typing import AsyncContextManager

import pytest

from tests.helpers.mcp_client import MCPClient, result_text


@pytest.fixture()
def misc_file(test_project_path: Path) -> Path:
    path = test_project_path / "MiscTools.lean"
    path.write_text(
        textwrap.dedent(
            """
            import Mathlib

            def miscValue : Nat := 0

            def multiAttemptTarget : Nat := 0

            -- Test axiom reporting
            theorem uses_propext (p q : Prop) (h : p ↔ q) : p = q := propext h
            theorem no_axioms : ∃ n : Nat, n > 0 := ⟨1, by norm_num⟩
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    return path


@pytest.mark.asyncio
async def test_misc_tools(
    mcp_client_factory: Callable[[], AsyncContextManager[MCPClient]],
    misc_file: Path,
    test_project_path: Path,
) -> None:
    async with mcp_client_factory() as client:
        build = await client.call_tool(
            "lean_build",
            {
                "lean_project_path": str(test_project_path),
            },
        )
        assert "Error during build" not in result_text(build)

        decl = await client.call_tool(
            "lean_declaration_file",
            {
                "file_path": str(misc_file),
                "symbol": "Nat",
            },
        )
        assert "Nat" in result_text(decl)

        multi = await client.call_tool(
            "lean_multi_attempt",
            {
                "file_path": str(misc_file),
                "line": 5,
                "snippets": [
                    "rfl",
                    "simp",
                ],
            },
        )
        multi_text = result_text(multi)
        assert "rfl" in multi_text or "simp" in multi_text

        run = await client.call_tool(
            "lean_run_code",
            {
                "code": """import Mathlib

#eval Nat.succ 0
""",
            },
        )
        run_text = result_text(run)
        assert "No diagnostics" in run_text or "severity" in run_text

        # Test axiom reporting
        axiom_test = await client.call_tool(
            "lean_axiom_report",
            {
                "file_path": str(misc_file),
                "declaration_name": "uses_propext",
            },
        )
        axiom_result = result_text(axiom_test)
        assert "propext" in axiom_result
        assert '"declaration": "uses_propext"' in axiom_result

        # Test theorem with no axioms (might report sorryAx in some cases)
        no_axiom_test = await client.call_tool(
            "lean_axiom_report",
            {
                "file_path": str(misc_file),
                "declaration_name": "no_axioms",
            },
        )
        no_axiom_result = result_text(no_axiom_test)
        assert '"declaration": "no_axioms"' in no_axiom_result
