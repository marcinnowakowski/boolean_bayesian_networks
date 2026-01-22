"""Analyze and visualize SCC graphs for biodivine networks."""

from pathlib import Path
from .scc_analyzer import SCCAnalyzer
from .scc_visualizer import SCCVisualizer


def analyze_biodivine_networks(output_dir: Path = None):
    """
    Analyze the three selected biodivine networks and generate SCC graphs.
    
    Args:
        output_dir: Directory to save output figures. If None, uses current dir.
    """
    # Paths
    base_path = Path(__file__).parent.parent
    biodivine_dir = base_path / "networks" / "functions" / "biodivine"
    
    if output_dir is None:
        output_dir = base_path / "scc_analysis" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Networks to analyze (with subdirectory paths)
    networks = [
        ("5d/bn_109_5d.py", "Caulobacter Cell Cycle (5D)"),
        ("7d/bn_158_7d.py", "Phage Lambda Decision (7D)"),
        ("10d/bn_063_10d_011.py", "Embryonic Development (10D)"),
    ]
    
    results = []
    
    for filename, description in networks:
        filepath = biodivine_dir / filename
        
        if not filepath.exists():
            print(f"Warning: {filepath} not found, skipping...")
            continue
        
        print(f"\nAnalyzing {description}...")
        print("-" * 50)
        
        # Analyze
        analyzer = SCCAnalyzer.from_file(filepath)
        sccs = analyzer.find_sccs()
        attractors, transient = analyzer.identify_attractors()
        scc_graph = analyzer.get_scc_graph()
        
        # Print summary
        print(f"  Total SCCs: {len(sccs)}")
        print(f"  Attractors: {len(attractors)}")
        print(f"  Transient SCCs: {len(transient)}")
        print(f"  SCC graph edges: {sum(len(v) for v in scc_graph.values())}")
        
        print(f"\n  Attractor sizes: {sorted([len(a) for a in attractors], reverse=True)}")
        transient_sizes = sorted([len(t) for t in transient], reverse=True)[:10]
        print(f"  Largest transient SCCs: {transient_sizes}")
        
        # Visualize
        visualizer = SCCVisualizer(analyzer)
        
        # Get just the filename without subdirectory
        base_filename = Path(filename).name.replace('.py', '')
        
        # Full graph (for smaller networks)
        if len(sccs) <= 50:
            save_path = output_dir / f"{base_filename}_scc_graph.png"
            visualizer.plot_scc_graph(
                title=f"SCC Graph: {description}",
                save_path=save_path,
                show=False
            )
            print(f"  Saved: {save_path}")
        
        # Simplified graph (for all networks)
        save_path = output_dir / f"{base_filename}_scc_simplified.png"
        visualizer.plot_simplified_scc_graph(
            title=f"Simplified SCC Graph: {description}",
            max_transient_sccs=15,
            save_path=save_path,
            show=False
        )
        print(f"  Saved: {save_path}")
        
        results.append({
            'filename': filename,
            'description': description,
            'num_sccs': len(sccs),
            'num_attractors': len(attractors),
            'num_transient': len(transient),
        })
    
    print("\n" + "=" * 50)
    print("Analysis complete!")
    return results


if __name__ == "__main__":
    analyze_biodivine_networks()
