#!/usr/bin/env python3
"""
Kappybara MCP Server

An MCP server for running Kappa simulations using the Kappybara package.
Accepts Kappa code as input and returns simulation results as CSV.
"""

import tempfile
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict
import io
import json
import sys

from fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("Kappa Simulator")


def run_kappa_simulation(
    kappa_code: str,
    time_limit: float = 100.0,
    points: int = 200,
    seed: Optional[int] = None
) -> str:
    """
    Run a Kappa simulation and return the results.

    Args:
        kappa_code: The Kappa model code to simulate
        time_limit: Maximum simulation time (default: 100.0)
        points: Number of data points to collect (default: 200)
        seed: Random seed for reproducibility (optional)

    Returns:
        JSON string with 'stdout', 'stderr', and 'output' (CSV) fields

    Example:
        ```
        kappa_code = '''
        %agent: A(x)
        %init: 1000 A()
        %obs: 'A' A()
        A(x), A(x) -> A(x!1), A(x!1) @ 0.001
        '''
        result = run_kappa_simulation(kappa_code, time_limit=50, points=100)
        ```
    """
    try:
        # Create a temporary directory for the simulation
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)

            # Write the Kappa code to a file
            input_file = tmppath / "input.ka"
            input_file.write_text(kappa_code)

            # Output file for CSV results
            output_file = tmppath / "output.csv"

            # Build the KaSim command
            # Try to use KaSim if available (faster), otherwise fall back to kappybara
            kasim_cmd = [
                "KaSim",
                "-i", str(input_file),
                "-o", str(output_file),
                "-t", str(time_limit),
                "-p", str(points)
            ]

            if seed is not None:
                kasim_cmd.extend(["-seed", str(seed)])

            # Try KaSim first
            try:
                result = subprocess.run(
                    kasim_cmd,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )

                # Check if KaSim succeeded
                if result.returncode == 0 and output_file.exists():
                    csv_content = output_file.read_text()
                    response = {
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                        "output": csv_content
                    }
                    return json.dumps(response)
                else:
                    # If KaSim failed, try kappybara
                    return run_with_kappybara(kappa_code, time_limit, points, seed, tmppath)

            except FileNotFoundError:
                # KaSim not installed, use kappybara
                return run_with_kappybara(kappa_code, time_limit, points, seed, tmppath)
            except subprocess.TimeoutExpired:
                error_response = {
                    "stdout": "",
                    "stderr": "Simulation timed out after 5 minutes",
                    "output": ""
                }
                return json.dumps(error_response)

    except Exception as e:
        error_response = {
            "stdout": "",
            "stderr": f"Simulation failed: {str(e)}",
            "output": ""
        }
        return json.dumps(error_response)


def run_with_kappybara(kappa_code: str, time_limit: float, points: int, seed: Optional[int], tmppath: Path) -> str:
    """
    Run simulation using kappybara Python library.

    Args:
        kappa_code: The Kappa model code
        time_limit: Maximum simulation time
        points: Number of data points
        seed: Random seed
        tmppath: Temporary directory path

    Returns:
        JSON string with stdout, stderr, and output (CSV) fields
    """
    stdout_capture = io.StringIO()
    stderr_capture = io.StringIO()

    try:
        from kappybara.system import System
        import random as rand

        # Set random seed if provided
        if seed is not None:
            rand.seed(seed)

        # Capture stdout/stderr during simulation
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = stdout_capture
        sys.stderr = stderr_capture

        try:
            # Parse and create the system from Kappa code
            system = System.from_ka(kappa_code)

            # The monitor is automatically created with the system
            # and tracks observables as we run update()

            # Run simulation until we reach the time limit
            while system.time < time_limit:
                system.update()

        finally:
            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        # Get the data from monitor as a dataframe
        df = system.monitor.dataframe

        # Convert to CSV string
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)
        csv_content = csv_buffer.getvalue()

        response = {
            "stdout": stdout_capture.getvalue(),
            "stderr": stderr_capture.getvalue(),
            "output": csv_content
        }
        return json.dumps(response)

    except ImportError as e:
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        error_response = {
            "stdout": stdout_capture.getvalue(),
            "stderr": f"Failed to import kappybara: {str(e)}. Please install kappybara: pip install kappybara",
            "output": ""
        }
        return json.dumps(error_response)
    except Exception as e:
        import traceback
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        error_response = {
            "stdout": stdout_capture.getvalue(),
            "stderr": f"Kappybara simulation failed: {str(e)}\n{traceback.format_exc()}",
            "output": ""
        }
        return json.dumps(error_response)


# Register the MCP tool
@mcp.tool()
def kappa_simulation(
    kappa_code: str,
    time_limit: float = 100.0,
    points: int = 200,
    seed: Optional[int] = None
) -> str:
    """
    Run a Kappa simulation and return the results.

    Args:
        kappa_code: The Kappa model code to simulate
        time_limit: Maximum simulation time (default: 100.0)
        points: Number of data points to collect (default: 200)
        seed: Random seed for reproducibility (optional)

    Returns:
        JSON string with 'stdout', 'stderr', and 'output' (CSV) fields
    """
    return run_kappa_simulation(kappa_code, time_limit, points, seed)


@mcp.resource("kappa://examples/simple")
def get_simple_example() -> str:
    """Get a simple reversible binding example Kappa model (kappybara syntax)"""
    return """
%init: 100 A(x[.])
%init: 100 B(x[.])

%obs: 'AB' |A(x[1]), B(x[1])|

A(x[.]), B(x[.]) <-> A(x[1]), B(x[1]) @ 1, 1
    """.strip()


@mcp.resource("kappa://examples/polymerization")
def get_polymerization_example() -> str:
    """Get a linear polymerization example (kappybara syntax)"""
    return """
%init: 1000 M(l[.], r[.])

%obs: 'Monomers' |M(l[.], r[.])|
%obs: 'Chains' |M(l[_])|

M(l[.], r[.]), M(l[.], r[.]) -> M(l[.], r[1]), M(l[1], r[.]) @ 0.001
    """.strip()


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
