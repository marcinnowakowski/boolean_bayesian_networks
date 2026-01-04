# Boolean Bayesian Networks

A Python utility for creating and analyzing truth tables for asynchronous boolean network transitions using NetworkX.

## Features

- Convert boolean network transitions to NetworkX directed graphs
- Generate comprehensive truth tables showing all possible state transitions
- Analyze network properties like cycles, attractors, and reachability
- Export truth tables in various formats (CSV, Excel, JSON)
- Visualize networks using matplotlib
- Compare multiple network configurations

## Installation

This project uses Poetry for dependency management. To install:

```bash
# Install Poetry if you haven't already
curl -sSL https://install.python-poetry.org | python3 -

# Install the project and dependencies
poetry install

# Activate the virtual environment
poetry shell
```

## Quick Start

```python
from boolean_networks.truth_table_generator import BooleanNetworkTruthTable

# Define your boolean network transitions
transitions = {
    "00": ["01", "10"],
    "01": ["11"],
    "10": ["00"],
    "11": ["01"]
}

# Create truth table generator
bn = BooleanNetworkTruthTable(transitions)

# Generate truth table
truth_table = bn.generate_truth_table()
print(truth_table)

# Analyze network properties
bn.print_summary()

# Export results
bn.export_truth_table('my_network.csv')
```

## Example Networks

The repository includes three pre-defined 4D boolean networks:

1. **Alternative Path Network** (`networks/alternative_path.py`): 10-cycle with one alternative path using 6 remaining states
2. **Reverse Cycle Network** (`networks/reverse_cycle.py`): 10-cycle with one reverse branch
3. **Small Cycles Network** (`networks/small_cycles.py`): 10-cycle with additional small cycles

## Usage Examples

Run the example analysis:

```bash
poetry run python examples/analyze_networks.py
```

Or use the command-line interface:

```bash
poetry run analyze-networks --help
```

## Development

```bash
# Run tests
poetry run pytest

# Format code
poetry run black .
poetry run isort .

# Type checking
poetry run mypy boolean_networks/

# Linting
poetry run flake8 boolean_networks/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.