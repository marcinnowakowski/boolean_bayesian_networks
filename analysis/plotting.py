import networkx as nx
import matplotlib.pyplot as plt
from analysis.utils import get_attractors


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
    for src, targets in true_transitions.items():
        for tgt in targets:
            G_true.add_edge(src, tgt)

    G_learned = nx.DiGraph()
    for src, targets in learned_transitions.items():
        for tgt in targets:
            G_learned.add_edge(src, tgt)

    # Identify attractors for coloring
    true_attrs = get_attractors(true_transitions)
    learned_attrs = get_attractors(learned_transitions)

    # Layout
    pos_true = nx.kamada_kawai_layout(G_true)
    pos_learned = nx.kamada_kawai_layout(G_learned)

    fig, axes = plt.subplots(1, 2, figsize=(18, 8))

    # Plot True
    color_map_true = [
        "red" if node in true_attrs else "skyblue" for node in G_true.nodes()
    ]
    nx.draw_networkx_nodes(
        G_true, pos_true, ax=axes[0], node_color=color_map_true, node_size=50
    )
    nx.draw_networkx_edges(
        G_true,
        pos_true,
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
        "red" if node in learned_attrs else "skyblue" for node in G_learned.nodes()
    ]
    nx.draw_networkx_nodes(
        G_learned, pos_learned, ax=axes[1], node_color=color_map_learned, node_size=50
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
        pos_learned,
        ax=axes[1],
        edge_color=edge_colors,
        alpha=0.6,
        arrows=True,
        arrowsize=10,
    )
    axes[1].set_title("Learned Dynamics", fontsize=14)
    axes[1].axis("off")

    from matplotlib.lines import Line2D

    legend_elements = [
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="red",
            markersize=10,
            label="Attractor State",
        ),
        Line2D(
            [0],
            [0],
            marker="o",
            color="w",
            markerfacecolor="skyblue",
            markersize=10,
            label="Transient State",
        ),
        Line2D([0], [0], color="green", lw=1, label="Correct Transition"),
        Line2D([0], [0], color="red", lw=1, label="Incorrect Transition"),
    ]
    axes[0].legend(handles=legend_elements, loc="upper left")

    plt.suptitle(title, fontsize=16)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
    print(f"Saved STG comparison to {save_path}")
