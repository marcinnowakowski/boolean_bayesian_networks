# Boolean Bayesian Networks

A Python toolkit for generating, analyzing, and transforming asynchronous Boolean networks. Supports conversion between network representations, function extraction, simplification using Quine-McCluskey algorithm, and network generation with configurable structural properties.

## Features

- **Network Generation**: Create random Boolean networks with specific structural properties
  - Standard generator with configurable attractors and parentless states
  - 3-dependency-limit generator ensuring each variable depends on at most 3 others
- **Format Conversions**: Transform between different network representations
  - Transitions → Truth Tables
  - Boolean Functions → Truth Tables  
  - Truth Tables → SOP (Sum of Products) expressions
- **Function Simplification**: Minimize Boolean expressions using Quine-McCluskey algorithm
- **Network Analysis**: Find attractors, fixed points, SCCs, and other structural properties
- **Visualization**: Network graph visualization with various layouts

## Installation

```bash
# Install Poetry if needed
curl -sSL https://install.python-poetry.org | python3 -

# Install project
poetry install
```

## Quick Start

### Generate a 7D Network with 3 Attractors

```bash
make generate_network SEED=42 OUT=networks/transitions/my_network.py
```

### Generate a Network with 3-Variable Dependency Limit

```bash
make generate_3dep SEED=35 OUT=networks/functions/my_3dep_network.py
```

### Convert Transitions to Boolean Functions (Full Pipeline)

```bash
# Step 1: Transitions → Truth Table
make transitions_to_truth_table FILE=networks/transitions/my_network.py OUT=networks/truth_tables/my_network.py

# Step 2: Truth Table → SOP Functions
make truth_table_to_sops FILE=networks/truth_tables/my_network.py OUT=networks/sops/my_network.py

# Step 3: Simplify SOP Functions
make simplify_sops FILE=networks/sops/my_network.py OUT=networks/simplified/my_network.py
```

## CLI Commands

All commands are available via `poetry run python -m boolean_networks.cli <command>`:

| Command | Description |
|---------|-------------|
| `generate-network` | Generate 7D network with configurable attractors |
| `generate-3dep` | Generate 7D network with 3-variable dependency limit |
| `transitions-to-truth-table` | Convert state transitions to truth table format |
| `functions-to-truth-table` | Convert Boolean functions to truth table format |
| `truth-table-to-sops` | Extract SOP expressions from truth table |
| `simplify-sops` | Simplify SOP expressions using Quine-McCluskey |
| `analyze` | Analyze a single network |
| `visualize` | Visualize network as a graph |

### Command Options

```bash
# Generate network with specific structure
poetry run python -m boolean_networks.cli generate-network \
    -s 42 \                    # Random seed
    -o output.py \             # Output file
    --attractors 3 \           # Number of attractors
    --attractor-size 4 \       # Size of each attractor
    --parentless 8             # Number of parentless states

# Generate network with 3-dependency limit
poetry run python -m boolean_networks.cli generate-3dep \
    -s 35 \                    # Random seed
    -o output.py \             # Output file
    --min-ones 2 \             # Min true outputs per function
    --max-ones 6               # Max true outputs per function
```

## Makefile Targets

```bash
make help                  # Show all available commands
make install               # Install dependencies
make test                  # Run tests
make generate_network      # Generate 7D network (SEED=, OUT=)
make generate_3dep         # Generate 7D network with 3-var limit (SEED=, OUT=)
make transitions_to_truth_table  # Convert transitions → truth table (FILE=, OUT=)
make functions_to_truth_table    # Convert functions → truth table (FILE=, OUT=)
make truth_table_to_sops         # Extract SOPs from truth table (FILE=, OUT=)
make simplify_sops               # Simplify SOP expressions (FILE=, OUT=)
make visualize                   # Visualize network (FILE=)
```

## File Formats

### Transitions Format
```python
transitions = {
    "0000000": ["0100000"],           # State → list of possible next states
    "0000001": ["0001001", "0100001"], # Async: can change one bit at a time
    ...
}
```

### Boolean Functions Format
```python
network_functions = {
    "x1": "(x2 & x3) | (~x4 & x5)",   # SOP expression
    "x2": "x1 & ~x3",
    ...
}
```

### Truth Table Format
```python
truth_table = {
    "0000000": {"x1": "1000000", "x2": "0100000", ...},  # state → {var: next_state_if_var_flips}
    ...
}
```

## Project Structure

```
boolean_networks/
├── cli.py                          # Command-line interface
├── transitions_generator/          # 7D network generator (structural approach)
├── generator_with_3_deps_limit/    # 7D network generator (function-based, 3-var limit)
├── truth_tables/                   # Truth table generation
│   ├── network_function_2_truth_table.py
│   └── transitions_2_truth_table.py
├── function_exctactor/             # Function extraction and simplification
│   ├── truth_table_2_functions.py  # Extract SOP from truth tables
│   └── sop_simplifier.py           # Quine-McCluskey simplification
└── old/                            # Legacy analysis tools

networks/
├── transitions/                    # Network transition definitions
│   ├── 4d_initial_analysis/
│   ├── 5d_interesting/
│   ├── 7d_generated/
│   └── 7d_recursive/
├── truth_tables/                   # Generated truth tables
├── sops/                           # Extracted SOP functions
└── functions/                      # Simplified/generated functions
    └── 7d_3dep/                    # Networks with 3-dependency limit
```

## Generators

### Standard Generator (`transitions_generator`)

Creates networks by defining structural regions:
- **Parentless states**: Sources with no incoming edges
- **SCC region**: Strongly connected component (transient states)
- **Attractors**: Isolated cycles that trap trajectories

```bash
make generate_network SEED=42 OUT=output.py
# Output: 128 states, 8 parentless, 3 attractors
```

### 3-Dependency Generator (`generator_with_3_deps_limit`)

Creates networks where each variable's update function depends on exactly 3 variables. This guarantees simpler Boolean expressions.

```bash
make generate_3dep SEED=35 OUT=output.py
# Output: Functions like "x1": "(~x2 & x3 & ~x5) | (x2 & x3 & x5)"
```

Good seeds with multiple attractors: 3, 26, 35, 40, 43

## Example: Full Pipeline

```bash
# 1. Generate a network with 3-dependency limit
make generate_3dep SEED=35 OUT=networks/functions/7d_3dep/bn_7d_3dep_seed_35.py

# Output includes both network_functions AND transitions:
# - x1 depends on: x2, x3, x5
# - x2 depends on: x1, x5, x7
# - ... (each variable depends on exactly 3 others)
# - 3 attractors (sizes: [64, 1, 1])
```

## Development

```bash
make test      # Run pytest
make lint      # Run flake8 + mypy  
make format    # Run black + isort
make check     # Run all checks
```

## License

MIT License
