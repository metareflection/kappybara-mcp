# Kappybara MCP Server

An MCP (Model Context Protocol) server for running Kappa simulations using the Kappybara package. This allows LLMs to run rule-based simulations of molecular interaction systems directly.

## Features

- **Run Kappa Simulations**: Execute Kappa models with customizable parameters using kappybara
- **CSV Output**: Get simulation results as CSV data for easy analysis
- **Example Models**: Built-in example models (reversible binding, linear polymerization)
- **Pure Python**: Uses the kappybara Python library for all simulations

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
%init: 100 A(x[.])
%init: 100 B(x[.])

%obs: 'AB' |A(x[1]), B(x[1])|

A(x[.]), B(x[.]) <-> A(x[1]), B(x[1]) @ 1, 1
"""

result = run_kappa_simulation(kappa_code, time_limit=50, points=100)
# Result is a JSON string like:
# {
#   "stdout": "",
#   "stderr": "",
#   "output": "time,AB\n0.0,0\n0.01,1\n..."
# }
```

### Available Resources

#### `kappa://examples/simple`
A simple reversible binding model (kappybara syntax).

#### `kappa://examples/polymerization`
A linear polymerization model (kappybara syntax).

## Kappa Language Basics (Kappybara Syntax)

Kappybara uses a specific syntax for Kappa models. Here's a quick reference:

### Basic Syntax

```kappa
%init: 100 AgentName(site1[.], site2[state])  # Initialize agents
%obs: 'Observable' |pattern|                   # Define observable
pattern -> pattern @ rate                      # Define rule (irreversible)
pattern <-> pattern @ rate1, rate2             # Define rule (reversible)
```

### Binding Sites
- `[.]` - unbound site
- `[1]`, `[2]`, etc. - bound sites (bond labels)
- `[_]` - wildcard for any binding state

### Example: Reversible Binding

```kappa
%init: 100 A(x[.])
%init: 100 B(x[.])

%obs: 'A_free' |A(x[.])|
%obs: 'B_free' |B(x[.])|
%obs: 'AB_complex' |A(x[1]), B(x[1])|

// Reversible binding with forward rate 0.001 and reverse rate 0.1
A(x[.]), B(x[.]) <-> A(x[1]), B(x[1]) @ 0.001, 0.1
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
2. LLMs can call the `run_kappa_simulation` tool with Kappa code (using kappybara syntax) and parameters
3. The server uses the Kappybara Python library to parse the model and run the simulation
4. Results are returned as JSON with stdout, stderr, and CSV output that can be analyzed or visualized

## References

- [Kappybara Documentation](https://kappybara.io/)
- [FastMCP Documentation](https://gofastmcp.com/)
- [Kappa Language](https://kappalanguage.org/)
- [Original ChatGPT Action](https://github.com/namin/Kappa-ChatGPT)

## License

MIT
