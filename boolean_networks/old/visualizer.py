"""
Visualization utilities for boolean networks.

This module provides the BooleanNetworkVisualizer class for creating various
visualizations of boolean network state transitions and structures.
"""

import networkx as nx
from typing import Dict, List


class BooleanNetworkVisualizer:
    """
    A class to handle visualization of boolean networks.
    """
    
    def __init__(self, graph: nx.DiGraph, transitions: Dict[str, List[str]], num_variables: int, all_states: List[str]):
        """
        Initialize the visualizer.
        
        Args:
            graph: NetworkX directed graph representing the network
            transitions: Dictionary mapping current states to lists of possible next states
            num_variables: Number of boolean variables
            all_states: List of all possible states
        """
        self.graph = graph
        self.transitions = transitions
        self.num_variables = num_variables
        self.all_states = all_states
    
    def visualize_network(self, filename: str = None, layout: str = 'spring'):
        """
        Visualize the network using NetworkX and matplotlib.
        
        Args:
            filename: Optional filename to save the plot
            layout: Layout algorithm ('spring', 'circular', 'shell', etc.)
        """
        try:
            import matplotlib.pyplot as plt
            
            plt.figure(figsize=(12, 8))
            
            if layout == 'spring':
                pos = nx.spring_layout(self.graph, k=1, iterations=50)
            elif layout == 'circular':
                pos = nx.circular_layout(self.graph)
            elif layout == 'shell':
                pos = nx.shell_layout(self.graph)
            else:
                pos = nx.spring_layout(self.graph)
            
            # Draw the network
            nx.draw(self.graph, pos, with_labels=True, node_color='lightblue',
                   node_size=1500, font_size=10, font_weight='bold',
                   arrows=True, arrowsize=20, edge_color='gray')
            
            plt.title("Boolean Network State Transitions")
            plt.axis('off')
            
            if filename:
                plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.show()
            
        except ImportError:
            print("matplotlib not available. Cannot visualize the network.")
    
    def visualize_hypercube_4d(self, filename: str = None, projection: str = 'stereographic'):
        """
        Visualize the 4D hypercube network with states positioned according to hypercube geometry.
        
        Args:
            filename: Optional filename to save the plot
            projection: Projection method ('stereographic', 'orthographic', 'grid')
        """
        if self.num_variables != 4:
            print(f"Hypercube visualization is designed for 4D networks. This network has {self.num_variables} variables.")
            return
            
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            # Create 4D hypercube coordinates
            def state_to_4d_coords(state_str):
                """Convert binary string to 4D coordinates."""
                return [int(bit) for bit in state_str]
            
            def project_4d_to_2d(coords_4d, method='stereographic'):
                """Project 4D coordinates to 2D for visualization."""
                x, y, z, w = coords_4d
                
                if method == 'stereographic':
                    # Stereographic projection from 4D to 2D
                    denom = 1 + w
                    if denom == 0:
                        denom = 0.1  # Avoid division by zero
                    proj_x = x / denom
                    proj_y = (y + z) / denom
                    return (proj_x, proj_y)
                
                elif method == 'orthographic':
                    # Simple orthographic projection (ignore z and w)
                    return (x + 0.5 * z, y + 0.5 * w)
                
                elif method == 'grid':
                    # Arrange in a 4x4 grid based on first two bits
                    grid_x = x + 2 * z
                    grid_y = y + 2 * w
                    return (grid_x, grid_y)
                
                else:
                    # Default to orthographic
                    return (x + 0.5 * z, y + 0.5 * w)
            
            # Generate positions for all states based on hypercube structure
            pos = {}
            coords_4d = {}
            
            for state in self.all_states:
                coords_4d[state] = state_to_4d_coords(state)
                pos[state] = project_4d_to_2d(coords_4d[state], projection)
            
            # Create the plot
            plt.figure(figsize=(14, 10))
            
            # Color nodes based on their position in the main cycle
            main_cycle = ["0000", "1000", "1100", "0100", "0110", "1110", "1010", "0010", "0011", "0001"]
            node_colors = []
            node_sizes = []
            
            for node in self.graph.nodes():
                if node in main_cycle:
                    node_colors.append('lightcoral')  # Main cycle nodes
                    node_sizes.append(2000)
                else:
                    node_colors.append('lightblue')   # Off-cycle nodes
                    node_sizes.append(1500)
            
            # Draw the hypercube edges (structural edges of the hypercube)
            hypercube_edges = []
            for state1 in self.all_states:
                coords1 = coords_4d[state1]
                for state2 in self.all_states:
                    coords2 = coords_4d[state2]
                    # Two states are connected in hypercube if they differ by exactly one bit
                    if sum(c1 != c2 for c1, c2 in zip(coords1, coords2)) == 1:
                        hypercube_edges.append((state1, state2))
            
            # Draw hypercube structure (light gray)
            nx.draw_networkx_edges(nx.Graph(hypercube_edges), pos, 
                                 edge_color='lightgray', alpha=0.3, width=0.5)
            
            # Draw the actual network transitions (colored by type)
            transition_edges = []
            branch_edges = []
            
            for source, targets in self.transitions.items():
                for target in targets:
                    if len(targets) > 1:
                        branch_edges.append((source, target))
                    else:
                        transition_edges.append((source, target))
            
            # Draw regular transitions
            if transition_edges:
                nx.draw_networkx_edges(self.graph, pos, edgelist=transition_edges,
                                     edge_color='blue', arrows=True, arrowsize=20,
                                     arrowstyle='->', width=2, alpha=0.8)
            
            # Draw branching transitions (different color)
            if branch_edges:
                nx.draw_networkx_edges(self.graph, pos, edgelist=branch_edges,
                                     edge_color='red', arrows=True, arrowsize=20,
                                     arrowstyle='->', width=2, alpha=0.8)
            
            # Draw nodes
            nx.draw_networkx_nodes(self.graph, pos, node_color=node_colors,
                                 node_size=node_sizes, alpha=0.9)
            
            # Draw labels
            nx.draw_networkx_labels(self.graph, pos, font_size=8, font_weight='bold')
            
            # Add title and legend
            plt.title(f"4D Hypercube Boolean Network\nProjection: {projection.title()}", 
                     fontsize=16, fontweight='bold')
            
            # Create legend
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', markerfacecolor='lightcoral', 
                       markersize=10, label='Main 10-cycle states'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', 
                       markersize=10, label='Off-cycle states'),
                Line2D([0], [0], color='blue', linewidth=2, label='Regular transitions'),
                Line2D([0], [0], color='red', linewidth=2, label='Branching transitions'),
                Line2D([0], [0], color='lightgray', linewidth=1, alpha=0.5, label='Hypercube edges')
            ]
            plt.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1.15, 1))
            
            plt.axis('equal')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            
            if filename:
                plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.show()
            
        except ImportError:
            print("matplotlib or numpy not available. Cannot visualize the hypercube.")
        except Exception as e:
            print(f"Error creating hypercube visualization: {e}")
    
    def visualize_hypercube_3d(self, filename: str = None, cube_separation: float = 2.0):
        """
        Visualize the 4D hypercube network as two connected 3D cubes in 3D space.
        The 4th dimension determines which cube (w=0 or w=1).
        
        Args:
            filename: Optional filename to save the plot
            cube_separation: Distance between the two 3D cubes along z-axis
        """
        if self.num_variables != 4:
            print(f"3D hypercube visualization is designed for 4D networks. This network has {self.num_variables} variables.")
            return
            
        try:
            import matplotlib.pyplot as plt
            from mpl_toolkits.mplot3d import Axes3D
            import numpy as np
            
            # Create 3D coordinates for each state
            def state_to_3d_coords(state_str, cube_separation):
                """Convert 4D binary string to 3D coordinates with two cubes."""
                x, y, z, w = [int(bit) for bit in state_str]
                # Place w=0 states in front cube, w=1 states in back cube
                # No offsets - pure hypercube geometry
                if w == 0:
                    # Front cube
                    base_x, base_y, base_z = x, y, z - cube_separation
                else:
                    # Back cube  
                    base_x, base_y, base_z = x, y, z
                
                # Apply offset to specific states
                offset_states = {'0000', '1000', '1100', '0100', '0010', '1010', '1110', '0110'}
                if state_str in offset_states:
                    base_x += 0.5
                    base_y += 1
                    base_z += 0
                
                # Return base coordinates without rotation
                return (base_x, base_y, base_z)
            
            # Generate 3D positions for all states
            pos_3d = {}
            coords_4d = {}
            
            for state in self.all_states:
                coords_4d[state] = [int(bit) for bit in state]
                pos_3d[state] = state_to_3d_coords(state, cube_separation)
            
            # Create the 3D plot
            fig = plt.figure(figsize=(16, 12))
            ax = fig.add_subplot(111, projection='3d')
            
            # Separate states into two cubes
            cube_0_states = [state for state in self.all_states if state[3] == '0']
            cube_1_states = [state for state in self.all_states if state[3] == '1']
            
            # Color coding
            main_cycle = ["0000", "1000", "1100", "0100", "0110", "1110", "1010", "0010", "0011", "0001"]
            
            def get_node_color_and_size(state):
                if state in main_cycle:
                    return 'red', 200
                else:
                    return 'lightblue', 150
            
            # Draw cube edges for both 3D cubes
            def draw_cube_edges(states, ax, alpha=0.2, color='gray'):
                """Draw the edges of a 3D cube."""
                cube_edges = []
                for state1 in states:
                    coords1 = coords_4d[state1][:3]  # Only x,y,z
                    for state2 in states:
                        coords2 = coords_4d[state2][:3]
                        # Two states are connected in 3D cube if they differ by exactly one bit in x,y,z
                        if sum(c1 != c2 for c1, c2 in zip(coords1, coords2)) == 1:
                            pos1 = pos_3d[state1]
                            pos2 = pos_3d[state2]
                            ax.plot([pos1[0], pos2[0]], [pos1[1], pos2[1]], [pos1[2], pos2[2]], 
                                   color=color, alpha=alpha, linewidth=1)
            
            # Draw 3D cube structures
            draw_cube_edges(cube_0_states, ax, alpha=0.3, color='lightgray')
            draw_cube_edges(cube_1_states, ax, alpha=0.3, color='lightgray')
            
            # Draw 4D connections (between corresponding vertices of the two cubes)
            for state0 in cube_0_states:
                corresponding_state1 = state0[:3] + '1'  # Change w=0 to w=1
                if corresponding_state1 in cube_1_states:
                    pos0 = pos_3d[state0]
                    pos1 = pos_3d[corresponding_state1]
                    ax.plot([pos0[0], pos1[0]], [pos0[1], pos1[1]], [pos0[2], pos1[2]], 
                           color='darkgray', alpha=0.4, linewidth=2, linestyle='--')
            
            # Draw network transitions
            # Define the main 10-cycle transitions
            main_cycle_transitions = [
                ('0000', '1000'), ('1000', '1100'), ('1100', '0100'), ('0100', '0110'),
                ('0110', '1110'), ('1110', '1010'), ('1010', '0010'), ('0010', '0011'),
                ('0011', '0001'), ('0001', '0000')
            ]
            main_cycle_set = set(main_cycle_transitions)
            
            cycle_edges = []
            other_edges = []
            
            for source, targets in self.transitions.items():
                for target in targets:
                    if (source, target) in main_cycle_set:
                        cycle_edges.append((source, target))
                    else:
                        other_edges.append((source, target))
            
            # Draw main 10-cycle transitions (thick red)
            for source, target in cycle_edges:
                pos_s = pos_3d[source]
                pos_t = pos_3d[target]
                
                # Use dashed line if connection involves 0000 or 0001
                linestyle = '--' if '0000' in [source, target] or '0001' in [source, target] else '-'
                
                ax.plot([pos_s[0], pos_t[0]], [pos_s[1], pos_t[1]], [pos_s[2], pos_t[2]], 
                       color='red', linewidth=4, alpha=0.9, linestyle=linestyle)
                
                # Add larger, more visible arrow at the end
                direction = np.array(pos_t) - np.array(pos_s)
                direction = direction / np.linalg.norm(direction) * 0.25
                ax.quiver(pos_t[0] - direction[0], pos_t[1] - direction[1], pos_t[2] - direction[2],
                         direction[0], direction[1], direction[2], 
                         color='darkred', alpha=1.0, arrow_length_ratio=0.6, linewidth=3)
            
            # Draw other transitions (thin blue)
            for source, target in other_edges:
                pos_s = pos_3d[source]
                pos_t = pos_3d[target]
                
                # Use dashed line if connection involves 0000 or 0001
                linestyle = '--' if '0000' in [source, target] or '0001' in [source, target] else '-'
                
                ax.plot([pos_s[0], pos_t[0]], [pos_s[1], pos_t[1]], [pos_s[2], pos_t[2]], 
                       color='blue', linewidth=1, alpha=0.8, linestyle=linestyle)
                
                # Add more visible arrow at the end
                direction = np.array(pos_t) - np.array(pos_s)
                direction = direction / np.linalg.norm(direction) * 0.2
                ax.quiver(pos_t[0] - direction[0], pos_t[1] - direction[1], pos_t[2] - direction[2],
                         direction[0], direction[1], direction[2], 
                         color='darkblue', alpha=1.0, arrow_length_ratio=0.5, linewidth=2)
            
            # Plot nodes with different colors and sizes
            for state in self.all_states:
                pos = pos_3d[state]
                color, size = get_node_color_and_size(state)
                ax.scatter(pos[0], pos[1], pos[2], c=color, s=size, alpha=0.8, edgecolor='black', linewidth=1)
                
                # Add state labels
                ax.text(pos[0], pos[1], pos[2], f'  {state}', fontsize=8, fontweight='bold')
            
            # Set labels and title
            ax.set_xlabel('X-axis (x coordinate)', fontweight='bold')
            ax.set_ylabel('Y-axis (y coordinate)', fontweight='bold')
            ax.set_zlabel('Z-axis (z + w*separation)', fontweight='bold')
            ax.set_title('4D Hypercube as Two Connected 3D Cubes\n(w=0 front cube, w=1 back cube)', 
                        fontsize=14, fontweight='bold')
            
            # Create custom legend
            from matplotlib.lines import Line2D
            legend_elements = [
                Line2D([0], [0], marker='o', color='w', markerfacecolor='red', 
                       markersize=10, label='Main 10-cycle states'),
                Line2D([0], [0], marker='o', color='w', markerfacecolor='lightblue', 
                       markersize=8, label='Off-cycle states'),
                Line2D([0], [0], color='red', linewidth=4, label='Main 10-cycle'),
                Line2D([0], [0], color='blue', linewidth=1, label='Other transitions'),
                Line2D([0], [0], color='lightgray', linewidth=1, alpha=0.5, label='3D cube edges'),
                Line2D([0], [0], color='darkgray', linewidth=2, linestyle='--', alpha=0.5, 
                       label='4D connections (vertical w=0 ↔ w=1)')
            ]
            ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0, 1))
            
            # Set equal aspect ratio and good viewing angle
            ax.set_box_aspect([1,1,cube_separation/2])
            
            # Ensure equal scale on x and y axes
            ax.set_xlim(-0.5, 2)
            ax.set_ylim(-0.5, 2)
            
            ax.view_init(elev=20, azim=45)  # Reset to normal viewing angle
            
            plt.tight_layout()
            
            if filename:
                plt.savefig(filename, dpi=300, bbox_inches='tight')
            plt.show()
            
        except ImportError:
            print("matplotlib or numpy not available. Cannot create 3D visualization.")
        except Exception as e:
            print(f"Error creating 3D hypercube visualization: {e}")