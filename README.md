# Kappybara MCP Server

An MCP (Model Context Protocol) server for running Kappa simulations using the Kappybara package. This allows LLMs to run rule-based simulations of molecular interaction systems directly.

## Features

- **Run Kappa Simulations**: Execute Kappa models with customizable parameters
- **CSV Output**: Get simulation results as CSV data for easy analysis
- **Example Models**: Built-in example models (simple binding, SIR epidemic model)
- **Dual Backend**: Uses KaSim binary if available (faster), falls back to Kappybara Python library

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Running the MCP Server

```bash
fastmcp run main.py
```

### Using with Claude Desktop

```
fastmcp install claude-desktop main.py
```

### Available Tools

#### `run_kappa_simulation`

Run a Kappa simulation and return results with stdout, stderr, and CSV output.

**Parameters:**
- `kappa_code` (string, required): The Kappa model code to simulate
- `time_limit` (float, default: 100.0): Maximum simulation time
- `points` (int, default: 200): Number of data points to collect
- `seed` (int, optional): Random seed for reproducibility

**Returns:** JSON string with three fields:
- `stdout`: Standard output from the simulation
- `stderr`: Standard error output (warnings, errors)
- `output`: CSV data with simulation results

**Example:**

```python
kappa_code = """
%agent: A(x)
%init: 1000 A()
%obs: 'A' A()

A(x), A(x) -> A(x!1), A(x!1) @ 0.001
"""

result = run_kappa_simulation(kappa_code, time_limit=50, points=100)
# Result is a JSON string like:
# {
#   "stdout": "...",
#   "stderr": "...",
#   "output": "time,A\n0.0,1000\n..."
# }
```

### Available Resources

#### `kappa://examples/simple`
A simple Kappa model demonstrating basic binding.

#### `kappa://examples/sir`
An SIR (Susceptible-Infected-Recovered) epidemic model.

## Kappa Language Basics

Kappa is a rule-based language for modeling molecular interactions. Here's a quick reference:

### Basic Syntax

```kappa
%agent: AgentName(site1, site2~state1~state2)  # Define agent types
%init: 100 AgentName()                          # Initialize agents
%obs: 'Observable' AgentName()                   # Define observable
Rule: pattern -> pattern @ rate                  # Define rule
```

### Example: Simple Binding

```kappa
%agent: A(x)
%agent: B(x)

%init: 100 A(x)
%init: 100 B(x)

%obs: 'A_free' A(x)
%obs: 'B_free' B(x)
%obs: 'AB_complex' A(x!1), B(x!1)

// Binding
A(x), B(x) -> A(x!1), B(x!1) @ 0.001

// Unbinding
A(x!1), B(x!1) -> A(x), B(x) @ 0.1
```

## Development

### Project Structure

```
kappybara-mcp/
├── main.py              # MCP server implementation
├── requirements.txt     # Python dependencies
├── README.md           # This file
└── test_example.py     # Example test/demo script
```

### Testing

Run the test example:
```bash
python test_example.py
```

## How It Works

1. The MCP server exposes Kappa simulation capabilities through the Model Context Protocol
2. LLMs can call the `run_kappa_simulation` tool with Kappa code and parameters
3. The server first tries to use KaSim (compiled binary) for faster execution
4. If KaSim is not available, it falls back to the Kappybara Python library
5. Results are returned as CSV data that can be analyzed or visualized

## References

- [Kappybara Documentation](https://kappybara.io/)
- [FastMCP Documentation](https://gofastmcp.com/)
- [Kappa Language](https://kappalanguage.org/)
- [Original ChatGPT Action](https://github.com/namin/Kappa-ChatGPT)

## License

MIT
