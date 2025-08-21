import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patheffects as pe
from matplotlib.ticker import MaxNLocator
import math
import numpy as np
import networkx as nx

class DataAnalysis:

    @staticmethod
    def tags_by_freq(tag_count, tag_number, *, save_figure=False):
        labels, counts = zip(*tag_count.most_common(tag_number))

        plt.figure(figsize=(8, 5))
        plt.bar(labels, counts, color="skyblue")
        plt.xticks(rotation=45, ha="right")
        plt.title(f"Top {tag_number} Tags by Frequency")
        plt.xlabel("Tag")
        plt.ylabel("Count")
        plt.tight_layout()
        if save_figure:
            plt.savefig(f"plots/top_{tag_number}_tags", dpi=300)
        plt.show()


    @staticmethod
    def tag_trends_line(index, series, str_type="month", *, save_figure=False):
        plt.figure(figsize=(12, 5))

        for tag, counts in series.items():
            plt.plot(index, counts, marker="o", label=tag)

        plt.title(f"Tag Frequency per {str_type.title()}")
        plt.xlabel("Time")
        plt.ylabel("Ticket Count")
        
        ax = plt.gca()
        if str_type.lower() == "month":
            ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
        elif str_type.lower() == "year":
            ax.xaxis.set_major_locator(mdates.YearLocator(base=1))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

        plt.xticks(rotation=45, ha="right")
        plt.legend(title="Tag", ncol=3)
        plt.legend(
            title="Tag",
            bbox_to_anchor=(1.05, 1),   # position: right side, top-aligned
            loc='upper left',
            borderaxespad=0.
        )
        plt.tight_layout()  # leave space on the right
        if save_figure:
            plt.savefig(f"plots/top_{len(series)}_tag_frequency_per_{str_type}_for_{len(index)}_{str_type}s", dpi=300)
        plt.show()
    

    @staticmethod
    def plot_cooccurrence_heatmap(matrix, labels, *, save_path="tag_pairs"):
        data = np.array(matrix, dtype=float)

        # mask the upper triangle (keep diagonal visible)
        mask = np.triu(np.ones_like(data, dtype=bool), k=1)
        data = np.ma.array(data, mask=mask)

        fig, ax = plt.subplots(figsize=(0.45*len(labels) + 3, 0.45*len(labels) + 3))

        # default colormap; simple and readable
        im = ax.imshow(data, aspect='equal')
        cbar = fig.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("Co-occurrence count", rotation=90, va="bottom", labelpad=15)
        cbar.ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # ticks and labels
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_yticklabels(labels)

        ax.set_title("Tag Pairs")
        ax.set_xlabel("Tag")
        ax.set_ylabel("Tag")

        # iterate over the lower triangle (and diagonal)
        iterator = ((i, j) for i in range(len(labels)) for j in range(len(labels))
                    if j <= i)
        for i, j in iterator:
            val = matrix[i][j]
            if val:  # skip zeros to reduce clutter
                ax.text(j, i, str(val), 
                        ha="center", va="center", 
                        fontsize=9, color="white",
                        path_effects=[pe.withStroke(linewidth=1.5, foreground="black")])
        
        plt.tight_layout()
        if save_path:
            plt.savefig(f"plots/{save_path}", dpi=300)
        plt.show()


    @staticmethod
    def plot_tag_network(
        matrix,
        labels,
        tag_counts,                 # dict/tag->count OR Counter
        *,                          # everything after this must be passed as a keyword argument
        min_edge=5,                 # hide weak edges
        show_isolates=True,         # draw isolated nodes (degree 0)
        base_node_size=50,          # points^2 baseline
        node_size_scale=100,        # multiplies sqrt(count)
        edge_scale=1,               # linewidth = 1 + edge_scale * weight
        seed=53,                    # reproducible layout
        save_path="tag_network"
        ):
        
        tag_number = len(labels)
        G = nx.Graph()

        # nodes
        # make sure every label has a numeric count (default 0)
        sizes = []
        for label in labels:
            count = int(tag_counts.get(label,0))
            size = base_node_size + node_size_scale * math.sqrt(count)
            G.add_node(label, count=count, size=size)
            sizes.append(size)

        # edges
        # only lower triangle needed; matrix is symmetric
        for i in range(tag_number):
            for j in range(i + 1, tag_number):
                weight = matrix[i][j]
                if weight >= min_edge:
                    G.add_edge(labels[i], labels[j], weight=weight)

        # optionally drop isolates
        if not show_isolates:
            isolates = [node for node, deg in G.degree() if deg == 0]
            G.remove_nodes_from(isolates)

        # layout & draw
        position = nx.spring_layout(G, seed=seed)  # force-directed

        plt.figure(figsize=(10, 7))
        # node sizes from graph data (recompute to align with any isolates removed)
        node_sizes = [G.nodes[tag_number]["size"] for tag_number in G.nodes]

        # edge widths proportional to weight
        edge_widths = [1 + edge_scale * G.edges[e]["weight"] for e in G.edges]

        nx.draw_networkx_edges(G, position, width=edge_widths, alpha=0.5)
        nx.draw_networkx_nodes(G, position, node_size=node_sizes)
        nx.draw_networkx_labels(G, position, font_size=9)

        plt.title("Tag Co-occurrence Network")
        plt.axis("off")
        plt.tight_layout()
        if save_path:
            plt.savefig(f"plots/{save_path}", dpi=300)
        plt.show()
