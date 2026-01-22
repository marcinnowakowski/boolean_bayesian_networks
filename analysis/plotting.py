import networkx as nx
import matplotlib.pyplot as plt
from analysis.utils import get_attractor_groups


def plot_structure_comparison(true_edges, learned_edges, title, save_path, num_vars=7):
    """
    Plots a graph overlaying True and Learned edges.
    """
    G = nx.DiGraph()
    # Add nodes x1..xn
    nodes = [f"x{i + 1}" for i in range(num_vars)]
    G.add_nodes_from(nodes)

    # Categorize edges
    tp_edges = true_edges.intersection(learned_edges)
    fp_edges = learned_edges - true_edges
    fn_edges = true_edges - learned_edges

    pos = nx.circular_layout(G)

    plt.figure(figsize=(10, 8))

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_color="skyblue", node_size=1000)
    nx.draw_networkx_labels(G, pos, font_size=16, font_weight="bold")

    # Draw edges with labels for legend (Method 2: Proxy Artists)
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=list(tp_edges),
        edge_color="green",
        width=2,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=20,
    )
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=list(fp_edges),
        edge_color="red",
        width=2,
        style="dotted",
        arrows=True,
        arrowstyle="-|>",
        arrowsize=20,
    )
    nx.draw_networkx_edges(
        G,
        pos,
        edgelist=list(fn_edges),
        edge_color="gray",
        width=1,
        style="dashed",
        alpha=0.5,
        arrows=True,
        arrowstyle="-|>",
        arrowsize=20,
    )

    # Proxy artists for legend
    from matplotlib.lines import Line2D

    legend_elements = [
        Line2D([0], [0], color="green", lw=2, label="True Positive"),
        Line2D([0], [0], color="red", lw=2, linestyle=":", label="False Positive"),
        Line2D([0], [0], color="gray", lw=1, linestyle="--", label="False Negative"),
    ]
    plt.legend(handles=legend_elements, loc="upper right")

    plt.title(title, fontsize=16)
    plt.axis("off")

    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"Saved structure plot to {save_path}")


def plot_stg_comparison(true_transitions, learned_transitions, title, save_path):
    """
    Plots State Transition Graphs side-by-side.
    Highlights edges in Learned graph: Green if matches True dynamics, Red otherwise.
    """
    # Build NetworkX graphs
    G_true = nx.DiGraph()
    G_true.add_nodes_from(
        true_transitions.keys()
    )  # Ensure all states are present even if isolated
    for src, targets in true_transitions.items():
        for tgt in targets:
            G_true.add_edge(src, tgt)

    G_learned = nx.DiGraph()
    G_learned.add_nodes_from(
        learned_transitions.keys()
    )  # Ensure all states are present
    for src, targets in learned_transitions.items():
        for tgt in targets:
            G_learned.add_edge(src, tgt)

    # Identify attractor groups for distinct coloring
    # true_groups is a list of sets
    true_groups = get_attractor_groups(true_transitions)
    learned_groups = get_attractor_groups(learned_transitions)

    # Sort true groups to ensure consistent coloring order (by first state in group)
    true_groups.sort(key=lambda g: sorted(list(g))[0])

    # Generate colors
    # distinct colors from matplotlib colormap
    prop_cycle = plt.rcParams["axes.prop_cycle"]
    colors = prop_cycle.by_key()["color"]  # typically 10 colors

    # Map nodes to colors
    # Default: skyblue
    node_colors_true = {node: "skyblue" for node in G_true.nodes()}
    node_colors_learned = {node: "skyblue" for node in G_learned.nodes()}

    true_group_colors = {}

    # Assign colors for True Attractors
    for i, group in enumerate(true_groups):
        color = colors[i % len(colors)]
        true_group_colors[i] = color
        for node in group:
            node_colors_true[node] = color

    # Assign colors for Learned Attractors
    has_incorrect_attractors = False
    for l_group in learned_groups:
        # Check if this learned group is exactly equal to any true group
        matched_idx = -1
        for t_idx, t_group in enumerate(true_groups):
            if l_group == t_group:
                matched_idx = t_idx
                break

        if matched_idx != -1:
            # Correct Group: Use same color
            color = true_group_colors[matched_idx]
            for node in l_group:
                node_colors_learned[node] = color
        else:
            # Incorrect Group: Use Red
            has_incorrect_attractors = True
            for node in l_group:
                node_colors_learned[node] = "red"

    # Layout: Use G_true to define positions for BOTH graphs for consistency
    pos = nx.kamada_kawai_layout(G_true)
    # pos = nx.spring_layout(G_true, k=0.15, seed=42)

    fig, axes = plt.subplots(1, 2, figsize=(18, 8))

    # Plot True
    color_map_true = [node_colors_true.get(node, "skyblue") for node in G_true.nodes()]
    nx.draw_networkx_nodes(
        G_true, pos, ax=axes[0], node_color=color_map_true, node_size=50
    )
    nx.draw_networkx_edges(
        G_true,
        pos,
        ax=axes[0],
        edge_color="gray",
        alpha=0.4,
        arrows=True,
        arrowsize=10,
    )
    axes[0].set_title("Ground Truth Dynamics", fontsize=14)
    axes[0].axis("off")

    # Plot Learned
    color_map_learned = [
        node_colors_learned.get(node, "skyblue") for node in G_learned.nodes()
    ]
    nx.draw_networkx_nodes(
        G_learned, pos, ax=axes[1], node_color=color_map_learned, node_size=50
    )

    # Color edges based on correctness
    edge_colors = []
    edges = G_learned.edges()
    for u, v in edges:
        if G_true.has_edge(u, v):
            edge_colors.append("green")
        else:
            edge_colors.append("red")

    nx.draw_networkx_edges(
        G_learned,
        pos,
        ax=axes[1],
        edge_color=edge_colors,
        alpha=0.6,
        arrows=True,
        arrowsize=10,
    )
    axes[1].set_title("Learned Dynamics", fontsize=14)
    axes[1].axis("off")

    from matplotlib.lines import Line2D

    legend_elements = []

    # Add True Attractor Groups to legend
    for i in range(len(true_groups)):
        legend_elements.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor=true_group_colors[i],
                markersize=10,
                label=f"Attractor Group {i + 1}",
            )
        )

    if has_incorrect_attractors:
        legend_elements.append(
            Line2D(
                [0],
                [0],
                marker="o",
                color="w",
                markerfacecolor="red",
                markersize=10,
                label="Incorrect Attractor",
            )
        )

    legend_elements.append(
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="skyblue",
            markersize=10,
            label="Transient State",
        )
    )
    legend_elements.append(
        Line2D([0], [0], color="green", lw=1, label="Correct Transition")
    )
    legend_elements.append(
        Line2D([0], [0], color="red", lw=1, label="Incorrect Transition")
    )

    axes[0].legend(handles=legend_elements, loc="upper left")

    plt.suptitle(title, fontsize=16)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"Saved STG comparison to {save_path}")
