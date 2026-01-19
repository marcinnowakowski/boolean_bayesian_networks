"""
Command-line interface for the Boolean Networks truth table generator.
"""

import argparse
import sys
from pathlib import Path
from typing import List

from .old.truth_table_generator import BooleanNetworkTruthTable
from .function_exctactor.network_loader import load_network_from_file


def analyze_single_network(filepath: str, output_dir: str = ".", export_format: str = "csv"):
    """Analyze a single network and export results."""
    try:
        print(f"Analyzing network: {filepath}")
        
        # Load the network
        transitions = load_network_from_file(filepath)
        bn = BooleanNetworkTruthTable(transitions)
        
        # Print summary
        bn.print_summary()
        
        # Generate truth table
        truth_table = bn.generate_truth_table()
        print(f"\nGenerated truth table with {len(truth_table)} rows")
        
        # Export results
        filename = Path(filepath).stem
        output_path = Path(output_dir) / f"{filename}_truth_table.{export_format}"
        bn.export_truth_table(str(output_path), export_format)
        print(f"Truth table exported to: {output_path}")
        
        # Export transition matrix
        matrix_path = Path(output_dir) / f"{filename}_transition_matrix.{export_format}"
        transition_matrix = bn.generate_state_transition_matrix()
        if export_format.lower() == 'csv':
            transition_matrix.to_csv(str(matrix_path))
        elif export_format.lower() == 'excel':
            transition_matrix.to_excel(str(matrix_path))
        print(f"Transition matrix exported to: {matrix_path}")
        
        return bn
        
    except Exception as e:
        print(f"Error analyzing {filepath}: {e}")
        return None


def analyze_all_networks(networks_dir: str = "networks", output_dir: str = "output"):
    """Analyze all networks in the networks directory."""
    networks_path = Path(networks_dir)
    
    if not networks_path.exists():
        print(f"Networks directory {networks_dir} does not exist.")
        return
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    # Find all Python files in networks directory
    network_files = list(networks_path.glob("*.py"))
    
    if not network_files:
        print(f"No network files found in {networks_dir}")
        return
    
    print(f"Found {len(network_files)} network files")
    print("=" * 80)
    
    results = []
    
    for network_file in network_files:
        bn = analyze_single_network(str(network_file), output_dir)
        if bn:
            results.append((network_file.stem, bn))
        print("-" * 80)
    
    # Generate comparison report
    if results:
        generate_comparison_report(results, output_dir)


def generate_comparison_report(results: List, output_dir: str):
    """Generate a comparison report for multiple networks."""
    import pandas as pd
    
    print("\n" + "=" * 80)
    print("NETWORK COMPARISON REPORT")
    print("=" * 80)
    
    comparison_data = []
    
    for name, bn in results:
        attractors = bn.find_attractors()
        truth_table = bn.generate_truth_table()
        
        # Calculate metrics
        num_defined_states = len([s for s in bn.all_states if s in bn.transitions])
        total_transitions = sum(len(next_states) for next_states in bn.transitions.values())
        avg_transitions_per_state = total_transitions / num_defined_states if num_defined_states > 0 else 0
        
        comparison_data.append({
            'Network': name,
            'Variables': bn.num_variables,
            'Defined States': num_defined_states,
            'Total Transitions': total_transitions,
            'Avg Transitions/State': round(avg_transitions_per_state, 2),
            'Fixed Points': len(attractors['fixed_points']),
            'Limit Cycles': len(attractors['cycles']),
            'Truth Table Rows': len(truth_table)
        })
    
    # Display and save comparison
    comparison_df = pd.DataFrame(comparison_data)
    print(comparison_df.to_string(index=False))
    
    # Save comparison report
    output_path = Path(output_dir) / "network_comparison.csv"
    comparison_df.to_csv(output_path, index=False)
    print(f"\nComparison report saved to: {output_path}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze boolean networks and generate truth tables"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Single network analysis
    single_parser = subparsers.add_parser('analyze', help='Analyze a single network')
    single_parser.add_argument('file', help='Path to the network file')
    single_parser.add_argument('-o', '--output', default='output', 
                              help='Output directory (default: output)')
    single_parser.add_argument('-f', '--format', choices=['csv', 'excel', 'json'],
                              default='csv', help='Export format (default: csv)')
    
    # Batch analysis
    batch_parser = subparsers.add_parser('analyze-all', help='Analyze all networks')
    batch_parser.add_argument('-n', '--networks-dir', default='networks',
                             help='Networks directory (default: networks)')
    batch_parser.add_argument('-o', '--output', default='output',
                             help='Output directory (default: output)')
    
    # Visualization
    viz_parser = subparsers.add_parser('visualize', help='Visualize a network')
    viz_parser.add_argument('file', help='Path to the network file')
    viz_parser.add_argument('-o', '--output', help='Output image file')
    viz_parser.add_argument('-l', '--layout', choices=['spring', 'circular', 'shell'],
                           default='spring', help='Layout algorithm (default: spring)')
    
    # Hypercube visualization
    hypercube_parser = subparsers.add_parser('hypercube', help='Visualize a 4D network on hypercube')
    hypercube_parser.add_argument('file', help='Path to the network file')
    hypercube_parser.add_argument('-o', '--output', help='Output image file')
    hypercube_parser.add_argument('-p', '--projection', choices=['stereographic', 'orthographic', 'grid'],
                                 default='stereographic', help='Projection method (default: stereographic)')
    
    # 3D hypercube visualization
    cube3d_parser = subparsers.add_parser('hypercube-3d', help='Visualize 4D network as two connected 3D cubes')
    cube3d_parser.add_argument('file', help='Path to the network file')
    cube3d_parser.add_argument('-o', '--output', help='Output image file')
    cube3d_parser.add_argument('-s', '--separation', type=float, default=2.0,
                              help='Distance between the two 3D cubes (default: 2.0)')
    
    # Truth table from functions
    tt_parser = subparsers.add_parser('functions-to-truth-table', help='Generate truth table from boolean functions')
    tt_parser.add_argument('file', help='Path to the functions file')
    tt_parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    
    # Truth table from transitions
    tt_trans_parser = subparsers.add_parser('transitions-to-truth-table', help='Generate truth table from transitions')
    tt_trans_parser.add_argument('file', help='Path to the transitions file')
    tt_trans_parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    
    # Functions from truth table
    fn_parser = subparsers.add_parser('truth-table-to-sops', help='Extract boolean functions from truth table')
    fn_parser.add_argument('file', help='Path to the truth table file')
    fn_parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    
    # Simplify SOPs
    simp_parser = subparsers.add_parser('simplify-sops', help='Simplify SOP expressions using Quine-McCluskey')
    simp_parser.add_argument('file', help='Path to the SOP functions file')
    simp_parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    
    # Generate network
    gen_parser = subparsers.add_parser('generate-network', help='Generate 7D network with specific structure')
    gen_parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    gen_parser.add_argument('-s', '--seed', type=int, help='Random seed')
    gen_parser.add_argument('--attractors', type=int, default=3, help='Number of attractors')
    gen_parser.add_argument('--attractor-size', type=int, default=4, help='Size of each attractor')
    gen_parser.add_argument('--parentless', type=int, default=8, help='Number of parentless states')
    
    # Generate network with 3-variable limit
    gen3_parser = subparsers.add_parser('generate-3dep', help='Generate network with 3-variable dependency limit')
    gen3_parser.add_argument('-o', '--output', help='Output file (default: stdout)')
    gen3_parser.add_argument('-s', '--seed', type=int, help='Random seed')
    gen3_parser.add_argument('-n', '--num-vars', type=int, default=7, help='Number of variables (default: 7)')
    gen3_parser.add_argument('--min-ones', type=int, default=2, help='Min true outputs per function')
    gen3_parser.add_argument('--max-ones', type=int, default=6, help='Max true outputs per function')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        analyze_single_network(args.file, args.output, args.format)
    elif args.command == 'analyze-all':
        analyze_all_networks(args.networks_dir, args.output)
    elif args.command == 'visualize':
        try:
            transitions = load_network_from_file(args.file)
            bn = BooleanNetworkTruthTable(transitions)
            bn.visualize_network(args.output, args.layout)
        except Exception as e:
            print(f"Error visualizing {args.file}: {e}")
    elif args.command == 'hypercube':
        try:
            transitions = load_network_from_file(args.file)
            bn = BooleanNetworkTruthTable(transitions)
            bn.visualize_hypercube_4d(args.output, args.projection)
        except Exception as e:
            print(f"Error creating hypercube visualization for {args.file}: {e}")
    elif args.command == 'hypercube-3d':
        try:
            transitions = load_network_from_file(args.file)
            bn = BooleanNetworkTruthTable(transitions)
            bn.visualize_hypercube_3d(args.output, args.separation)
        except Exception as e:
            print(f"Error creating 3D hypercube visualization for {args.file}: {e}")
    elif args.command == 'functions-to-truth-table':
        try:
            from .truth_tables import load_functions, generate_truth_table, truth_table_to_string
            functions = load_functions(args.file)
            
            # Build output
            lines = ['"""']
            lines.append(f"Truth table generated from: {args.file}")
            lines.append("")
            lines.append("Format: state -> {variable: next state if this variable is activated}")

            lines.append("")
            lines.append('Functions:')
            for var in sorted(functions.keys()):
                lines.append(f"  {var}' = {functions[var]}")
            lines.append('"""')
            lines.append('')
            
            truth_table = generate_truth_table(functions)
            lines.append(truth_table_to_string(truth_table))
            output = '\n'.join(lines)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Truth table written to {args.output}")
            else:
                print(output)
        except Exception as e:
            print(f"Error generating truth table from {args.file}: {e}")
    elif args.command == 'transitions-to-truth-table':
        try:
            from .truth_tables import load_transitions, transitions_to_truth_table, truth_table_to_string
            transitions = load_transitions(args.file)
            
            # Build output
            lines = ['"""']
            lines.append(f"Truth table generated from: {args.file}")
            lines.append("")
            lines.append("Format: state -> {variable: next_state_if_that_var_changes}")
            lines.append("Missing transitions are treated as self-loops.")
            lines.append('"""')
            lines.append('')
            
            truth_table = transitions_to_truth_table(transitions)
            lines.append(truth_table_to_string(truth_table))
            output = '\n'.join(lines)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Truth table written to {args.output}")
            else:
                print(output)
        except Exception as e:
            print(f"Error generating truth table from {args.file}: {e}")
    elif args.command == 'truth-table-to-sops':
        try:
            from .function_exctactor.truth_table_2_functions import load_truth_table, extract_functions, functions_to_string
            truth_table = load_truth_table(args.file)
            functions = extract_functions(truth_table)
            output = functions_to_string(functions, args.file)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Functions written to {args.output}")
            else:
                print(output)
        except Exception as e:
            print(f"Error extracting functions from {args.file}: {e}")
    elif args.command == 'simplify-sops':
        try:
            from .function_exctactor.sop_simplifier import load_sops, simplify_all, functions_to_string
            functions = load_sops(args.file)
            simplified = simplify_all(functions)
            output = functions_to_string(simplified, args.file)
            
            if args.output:
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Simplified functions written to {args.output}")
            else:
                print(output)
        except Exception as e:
            print(f"Error simplifying functions from {args.file}: {e}")
    elif args.command == 'generate-network':
        try:
            from .transitions_generator import generate_network, NetworkConfig
            from .transitions_generator.generator import network_to_string, analyze_network
            
            config = NetworkConfig(
                seed=args.seed,
                num_attractors=args.attractors,
                attractor_size=args.attractor_size,
                num_parentless=args.parentless,
            )
            
            transitions = generate_network(config)
            analysis = analyze_network(transitions)
            
            print(f"Generated network:")
            print(f"  States: {analysis['num_states']}")
            print(f"  Parentless: {analysis['parentless_states']}")
            print(f"  Attractors: {analysis['num_attractors']} (sizes: {analysis['attractor_sizes']})")
            
            output = network_to_string(transitions, f"generated_7d_seed_{args.seed or 'random'}")
            
            if args.output:
                import os
                os.makedirs(os.path.dirname(args.output), exist_ok=True)
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Network written to {args.output}")
            else:
                print(output)
        except Exception as e:
            print(f"Error generating network: {e}")
    elif args.command == 'generate-3dep':
        try:
            from .generator_with_3_deps_limit import generate_network, NetworkConfig, analyze_network
            from .generator_with_3_deps_limit.generator import network_to_string
            
            config = NetworkConfig(
                num_vars=args.num_vars,
                seed=args.seed,
                min_true_outputs=args.min_ones,
                max_true_outputs=args.max_ones,
            )
            
            transitions, functions = generate_network(config)
            analysis = analyze_network(transitions)
            
            print(f"Generated network ({args.num_vars}D, 3-dep limit):")
            print(f"  States: {analysis['num_states']}")
            print(f"  Fixed points: {analysis['fixed_points']}")
            print(f"  Attractors: {analysis['num_attractors']} (sizes: {analysis['attractor_sizes']})")
            
            # Show dependencies
            print(f"  Dependencies:")
            for var_name, (deps, _) in sorted(functions.items()):
                dep_names = [f"x{d + 1}" for d in deps]
                print(f"    {var_name} <- {', '.join(dep_names)}")
            
            output = network_to_string(transitions, functions, f"generated_{args.num_vars}d_3dep_seed_{args.seed or 'random'}")
            
            if args.output:
                import os
                os.makedirs(os.path.dirname(args.output), exist_ok=True)
                with open(args.output, 'w') as f:
                    f.write(output)
                print(f"Network written to {args.output}")
            else:
                print(output)
        except Exception as e:
            print(f"Error generating 3-dep network: {e}")
            import traceback
            traceback.print_exc()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()