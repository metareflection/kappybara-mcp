#!/usr/bin/env python3
"""
Test example for Kappybara MCP Server

This script demonstrates how to use the run_kappa_simulation function directly
without going through the MCP protocol (useful for testing).
"""

import json
from main import run_kappa_simulation


def print_result(result_json: str, title: str):
    """Pretty print the simulation result"""
    result = json.loads(result_json)

    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")

    if result["stdout"]:
        print(f"\n--- STDOUT ---")
        print(result["stdout"])

    if result["stderr"]:
        print(f"\n--- STDERR ---")
        print(result["stderr"])

    if result["output"]:
        print(f"\n--- OUTPUT (CSV) ---")
        # Print first few lines of CSV
        lines = result["output"].strip().split('\n')
        for i, line in enumerate(lines[:10]):
            print(line)
        if len(lines) > 10:
            print(f"... ({len(lines) - 10} more lines)")


def example_simple_binding():
    """Example 1: Reversible binding model (kappybara syntax)"""
    kappa_code = """
%init: 10 A(x[.])
%init: 10 B(x[.])

%obs: 'A_free' |A(x[.])|
%obs: 'B_free' |B(x[.])|
%obs: 'AB_complex' |A(x[1]), B(x[1])|

A(x[.]), B(x[.]) <-> A(x[1]), B(x[1]) @ 1, 1
"""

    result = run_kappa_simulation(
        kappa_code=kappa_code,
        time_limit=2.0,
        points=20
    )

    print_result(result, "Example 1: Reversible Binding")


def example_polymerization():
    """Example 2: Linear polymerization model (kappybara syntax)"""
    kappa_code = """
%init: 100 M(l[.], r[.])

%obs: 'Monomers' |M(l[.], r[.])|
%obs: 'Dimers' |M(l[.], r[1]), M(l[1], r[.])|

M(l[.], r[.]), M(l[.], r[.]) -> M(l[.], r[1]), M(l[1], r[.]) @ 0.01
"""

    result = run_kappa_simulation(
        kappa_code=kappa_code,
        time_limit=10.0,
        points=20,
        seed=42  # For reproducibility
    )

    print_result(result, "Example 2: Linear Polymerization")


def example_invalid_code():
    """Example 3: Invalid Kappa code (to test error handling)"""
    kappa_code = """
This is not valid Kappa code!
"""

    result = run_kappa_simulation(
        kappa_code=kappa_code,
        time_limit=10.0,
        points=10
    )

    print_result(result, "Example 3: Invalid Code (Error Handling)")


if __name__ == "__main__":
    print("Testing Kappybara MCP Server")
    print("="*60)

    # Run examples
    example_simple_binding()
    example_polymerization()
    example_invalid_code()

    print("\n" + "="*60)
    print("Testing complete!")
    print("="*60)
