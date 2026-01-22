"""SCC Visualization module for Boolean Networks."""

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import networkx as nx
from typing import Dict, List, Set, Optional, Tuple
from pathlib import Path

from .scc_analyzer import SCCAnalyzer


class SCCVisualizer:
    """Visualize SCC graphs of Boolean networks."""
    
    def __init__(self, analyzer: SCCAnalyzer):
        """
        Initialize visualizer with an analyzer.
        
        Args:
            analyzer: SCCAnalyzer instance
        """
        self.analyzer = analyzer
    
    def create_scc_graph(self) -> nx.DiGraph:
        """Create NetworkX DiGraph of the SCC condensation."""
        scc_graph = self.analyzer.get_scc_graph()
        sccs = self.analyzer.find_sccs()
        attractors, transient = self.analyzer.identify_attractors()
        attractor_set = {frozenset(a) for a in attractors}
        
        G = nx.DiGraph()
        
        # Add nodes with attributes
        for i, scc in enumerate(sccs):
            is_attractor = frozenset(scc) in attractor_set
            G.add_node(i, 
                       size=len(scc),
                       is_attractor=is_attractor,
                       label=f"{len(scc)}")
        
        # Add edges
        for src, dsts in scc_graph.items():
            for dst in dsts:
                G.add_edge(src, dst)
        
        return G
    
    def plot_scc_graph(self, 
                       title: str = "SCC Graph",
                       figsize: Tuple[int, int] = (12, 10),
                       save_path: Optional[Path] = None,
                       show: bool = True,
                       node_size_scale: float = 100,
                       min_node_size: int = 300,
                       max_node_size: int = 3000) -> plt.Figure:
        """
        Plot the SCC condensation graph.
        
        Args:
            title: Plot title
            figsize: Figure size
            save_path: Path to save the figure
            show: Whether to display the plot
            node_size_scale: Scale factor for node sizes
            min_node_size: Minimum node size
            max_node_size: Maximum node size
        
        Returns:
            matplotlib Figure
        """
        G = self.create_scc_graph()
        
        if len(G.nodes()) == 0:
            fig, ax = plt.subplots(figsize=figsize)
            ax.text(0.5, 0.5, "No SCCs found", ha='center', va='center')
            ax.set_title(title)
            return fig
        
        fig, ax = plt.subplots(figsize=figsize)
        
        # Compute layout - use hierarchical layout for DAG
        try:
            # Try topological generations for layered layout
            pos = nx.nx_agraph.graphviz_layout(G, prog='dot')
        except:
            try:
                pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
            except:
                pos = nx.kamada_kawai_layout(G)
        
        # Prepare node colors and sizes
        node_colors = []
        node_sizes = []
        
        for node in G.nodes():
            size = G.nodes[node]['size']
            is_attractor = G.nodes[node]['is_attractor']
            
            # Color: attractors are green, transient are blue
            if is_attractor:
                node_colors.append('#2ecc71')  # Green
            else:
                node_colors.append('#3498db')  # Blue
            
            # Size based on SCC size (log scale for large differences)
            import math
            scaled_size = min_node_size + node_size_scale * math.log2(size + 1)
            node_sizes.append(min(scaled_size, max_node_size))
        
        # Draw the graph
        nx.draw_networkx_nodes(G, pos, ax=ax,
                               node_color=node_colors,
                               node_size=node_sizes,
                               alpha=0.8)
        
        nx.draw_networkx_edges(G, pos, ax=ax,
                               edge_color='gray',
                               arrows=True,
                               arrowsize=15,
                               alpha=0.6,
                               connectionstyle="arc3,rad=0.1")
        
        # Add labels (SCC sizes)
        labels = {node: G.nodes[node]['label'] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, ax=ax, 
                                font_size=8, font_weight='bold')
        
        # Legend
        attractor_patch = mpatches.Patch(color='#2ecc71', label='Attractor')
        transient_patch = mpatches.Patch(color='#3498db', label='Transient SCC')
        ax.legend(handles=[attractor_patch, transient_patch], loc='upper left')
        
        ax.set_title(title)
        ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        
        if show:
            plt.show()
        
        return fig
    
    def plot_simplified_scc_graph(self,
                                   title: str = "Simplified SCC Graph",
                                   max_transient_sccs: int = 20,
                                   figsize: Tuple[int, int] = (12, 10),
                                   save_path: Optional[Path] = None,
                                   show: bool = True) -> plt.Figure:
        """
        Plot a simplified SCC graph showing only largest SCCs.
        
        For networks with many SCCs, this shows:
        - All attractors
        - Top N largest transient SCCs
        - Aggregated "other" node for remaining SCCs
        
        Args:
            title: Plot title
            max_transient_sccs: Maximum number of transient SCCs to show
            figsize: Figure size
            save_path: Path to save figure
            show: Whether to display
        
        Returns:
            matplotlib Figure
        """
        sccs = self.analyzer.find_sccs()
        scc_graph = self.analyzer.get_scc_graph()
        attractors, transient = self.analyzer.identify_attractors()
        
        # Get attractor indices
        state_to_scc = self.analyzer.get_state_to_scc_mapping()
        attractor_indices = set()
        for att in attractors:
            sample_state = next(iter(att))
            attractor_indices.add(state_to_scc[sample_state])
        
        # Sort transient SCCs by size
        transient_with_idx = []
        for i, scc in enumerate(sccs):
            if i not in attractor_indices:
                transient_with_idx.append((i, len(scc)))
        transient_with_idx.sort(key=lambda x: -x[1])
        
        # Select top transient SCCs
        show_transient = set(idx for idx, _ in transient_with_idx[:max_transient_sccs])
        hidden_transient = set(idx for idx, _ in transient_with_idx[max_transient_sccs:])
        
        # Build simplified graph
        G = nx.DiGraph()
        
        # Add attractor nodes
        for i in attractor_indices:
            G.add_node(f"A{i}", size=len(sccs[i]), is_attractor=True,
                       label=f"A\n{len(sccs[i])}")
        
        # Add visible transient nodes
        for i in show_transient:
            G.add_node(f"T{i}", size=len(sccs[i]), is_attractor=False,
                       label=str(len(sccs[i])))
        
        # Add aggregated "other" node if there are hidden SCCs
        if hidden_transient:
            total_hidden = sum(len(sccs[i]) for i in hidden_transient)
            G.add_node("other", size=total_hidden, is_attractor=False,
                       label=f"...{len(hidden_transient)}\nSCCs")
        
        # Add edges
        node_mapping = {}
        for i in attractor_indices:
            node_mapping[i] = f"A{i}"
        for i in show_transient:
            node_mapping[i] = f"T{i}"
        for i in hidden_transient:
            node_mapping[i] = "other"
        
        for src, dsts in scc_graph.items():
            src_node = node_mapping.get(src)
            if src_node:
                for dst in dsts:
                    dst_node = node_mapping.get(dst)
                    if dst_node and src_node != dst_node:
                        if not G.has_edge(src_node, dst_node):
                            G.add_edge(src_node, dst_node)
        
        # Plot
        fig, ax = plt.subplots(figsize=figsize)
        
        if len(G.nodes()) == 0:
            ax.text(0.5, 0.5, "No SCCs to display", ha='center', va='center')
            ax.set_title(title)
            return fig
        
        try:
            pos = nx.spring_layout(G, k=3, iterations=50, seed=42)
        except:
            pos = nx.circular_layout(G)
        
        # Colors and sizes
        node_colors = []
        node_sizes = []
        
        for node in G.nodes():
            is_att = G.nodes[node].get('is_attractor', False)
            size = G.nodes[node].get('size', 1)
            
            if node == "other":
                node_colors.append('#95a5a6')  # Gray
            elif is_att:
                node_colors.append('#2ecc71')  # Green
            else:
                node_colors.append('#3498db')  # Blue
            
            import math
            node_sizes.append(300 + 100 * math.log2(size + 1))
        
        nx.draw_networkx_nodes(G, pos, ax=ax,
                               node_color=node_colors,
                               node_size=node_sizes,
                               alpha=0.8)
        
        nx.draw_networkx_edges(G, pos, ax=ax,
                               edge_color='gray',
                               arrows=True,
                               arrowsize=15,
                               alpha=0.6)
        
        labels = {node: G.nodes[node]['label'] for node in G.nodes()}
        nx.draw_networkx_labels(G, pos, labels, ax=ax,
                                font_size=8, font_weight='bold')
        
        # Legend
        patches = [
            mpatches.Patch(color='#2ecc71', label='Attractor'),
            mpatches.Patch(color='#3498db', label='Transient SCC'),
        ]
        if hidden_transient:
            patches.append(mpatches.Patch(color='#95a5a6', label='Other SCCs'))
        ax.legend(handles=patches, loc='upper left')
        
        ax.set_title(title)
        ax.axis('off')
        
        plt.tight_layout()
        
        if save_path:
            fig.savefig(save_path, dpi=150, bbox_inches='tight')
        
        if show:
            plt.show()
        
        return fig
