"""
LAL (Lean Auto Linter) integration utilities.

Provides binary discovery and execution for auto-fixing mechanical linter warnings.
"""

import subprocess
import os
from pathlib import Path
from typing import Optional


def find_lal_binary(project_path: Path) -> Optional[str]:
    """
    Find LAL binary, checking environment variable and common locations.

    Search order:
    1. LAL_PATH environment variable
    2. Project's .lake/build/bin/lal
    3. Sibling LAL directory (../LAL/.lake/build/bin/lal)

    Args:
        project_path: Path to the Lean project

    Returns:
        Path to LAL binary if found, None otherwise
    """
    # 1. Environment variable
    if lal_path := os.environ.get("LAL_PATH"):
        if Path(lal_path).exists():
            return lal_path

    # 2. Project's .lake/build/bin/lal
    project_lal = project_path / ".lake" / "build" / "bin" / "lal"
    if project_lal.exists():
        return str(project_lal)

    # 3. Sibling LAL directory
    sibling_lal = project_path.parent / "LAL" / ".lake" / "build" / "bin" / "lal"
    if sibling_lal.exists():
        return str(sibling_lal)

    return None


def run_lal(
    lal_path: str,
    file_path: str,
    dry_run: bool = True,
    recursive: bool = False,
    glob_pattern: Optional[str] = None,
    timeout: int = 60
) -> dict:
    """
    Execute LAL on a file or directory and return results.

    Args:
        lal_path: Path to LAL binary
        file_path: Absolute path to Lean file or directory
        dry_run: If True, show fixes without applying
        recursive: If True and path is directory, process recursively
        glob_pattern: Filter files by pattern (e.g., "**/*.lean")
        timeout: Command timeout in seconds

    Returns:
        Dictionary with 'success' boolean and either 'output' or 'error'
    """
    cmd = [lal_path, "--json"]
    if dry_run:
        cmd.append("--dry-run")
    if recursive:
        cmd.append("--recursive")
    if glob_pattern:
        cmd.extend(["--glob", glob_pattern])
    cmd.append(file_path)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            return {"success": True, "output": result.stdout}
        else:
            return {
                "success": False,
                "error": result.stderr or f"LAL exited with code {result.returncode}"
            }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"LAL timed out after {timeout}s"}
    except FileNotFoundError:
        return {"success": False, "error": f"LAL binary not found at {lal_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_lal_sorry(
    lal_path: str,
    file_path: str,
    verbose: bool = False,
    recursive: bool = False,
    glob_pattern: Optional[str] = None,
    timeout: int = 60
) -> dict:
    """
    Execute LAL sorry command and return results.

    Args:
        lal_path: Path to LAL binary
        file_path: Absolute path to Lean file or directory
        verbose: If True, include declaration and goal fields
        recursive: If True and path is directory, process recursively
        glob_pattern: Filter files by pattern (e.g., "**/*.lean")
        timeout: Command timeout in seconds

    Returns:
        Dictionary with 'success' boolean and either 'output' or 'error'
    """
    cmd = [lal_path, "sorry"]
    if verbose:
        cmd.append("--verbose")
    if recursive:
        cmd.append("--recursive")
    if glob_pattern:
        cmd.extend(["--glob", glob_pattern])
    cmd.append(file_path)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            return {"success": True, "output": result.stdout}
        else:
            return {
                "success": False,
                "error": result.stderr or f"LAL exited with code {result.returncode}"
            }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"LAL timed out after {timeout}s"}
    except FileNotFoundError:
        return {"success": False, "error": f"LAL binary not found at {lal_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_lal_deps(
    lal_path: str,
    file_path: str,
    recursive: bool = False,
    glob_pattern: Optional[str] = None,
    timeout: int = 60
) -> dict:
    """
    Execute LAL deps command and return results.

    Args:
        lal_path: Path to LAL binary
        file_path: Absolute path to Lean file or directory
        recursive: If True and path is directory, process recursively
        glob_pattern: Filter files by pattern (e.g., "**/*.lean")
        timeout: Command timeout in seconds

    Returns:
        Dictionary with 'success' boolean and either 'output' or 'error'
    """
    cmd = [lal_path, "deps"]
    if recursive:
        cmd.append("--recursive")
    if glob_pattern:
        cmd.extend(["--glob", glob_pattern])
    cmd.append(file_path)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            return {"success": True, "output": result.stdout}
        else:
            return {
                "success": False,
                "error": result.stderr or f"LAL exited with code {result.returncode}"
            }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"LAL timed out after {timeout}s"}
    except FileNotFoundError:
        return {"success": False, "error": f"LAL binary not found at {lal_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def run_lal_trivial(
    lal_path: str,
    file_path: str,
    recursive: bool = False,
    glob_pattern: Optional[str] = None,
    timeout: int = 60
) -> dict:
    """
    Execute LAL trivial command and return results.

    Args:
        lal_path: Path to LAL binary
        file_path: Absolute path to Lean file or directory
        recursive: If True and path is directory, process recursively
        glob_pattern: Filter files by pattern (e.g., "**/*.lean")
        timeout: Command timeout in seconds

    Returns:
        Dictionary with 'success' boolean and either 'output' or 'error'
    """
    cmd = [lal_path, "trivial"]
    if recursive:
        cmd.append("--recursive")
    if glob_pattern:
        cmd.extend(["--glob", glob_pattern])
    cmd.append(file_path)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout
        )

        if result.returncode == 0:
            return {"success": True, "output": result.stdout}
        else:
            return {
                "success": False,
                "error": result.stderr or f"LAL exited with code {result.returncode}"
            }

    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"LAL timed out after {timeout}s"}
    except FileNotFoundError:
        return {"success": False, "error": f"LAL binary not found at {lal_path}"}
    except Exception as e:
        return {"success": False, "error": str(e)}
