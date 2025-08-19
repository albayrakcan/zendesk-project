import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.patheffects as pe
from matplotlib.ticker import MaxNLocator
import numpy as np

class DataAnalysis:

    @staticmethod
    def tags_by_freq(tag_count, n):
        labels, counts = zip(*tag_count.most_common(n))

        plt.figure(figsize=(8, 5))
        plt.bar(labels, counts, color="skyblue")
        plt.xticks(rotation=45, ha="right")
        plt.title(f"Top {n} Tags by Frequency")
        plt.xlabel("Tag")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.savefig(f"plots/top_{n}_tags.png", dpi=300)
        plt.show()


    @staticmethod
    def tag_trends_line(index, series, str_type="month"):
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

        plt.savefig(f"plots/top_{len(series)}_tag_frequency_per_{str_type}_for_{len(index)}_{str_type}s.png", dpi=300)
        plt.show()


    @staticmethod
    def plot_tag_network(matrix, labels, tag_counts, min_edge=2):
        ...

    
    @staticmethod
    def plot_cooccurrence_heatmap(matrix, labels):
        data = np.array(matrix, dtype=float)

        # Optional: mask the upper triangle (keep diagonal visible)
        mask = np.triu(np.ones_like(data, dtype=bool), k=1)
        data = np.ma.array(data, mask=mask)

        fig, ax = plt.subplots(figsize=(0.45*len(labels) + 3, 0.45*len(labels) + 3))

        # default colormap; simple and readable
        im = ax.imshow(data, aspect='equal')
        cbar = fig.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("Co-occurrence count", rotation=90, va="bottom", labelpad=15)
        cbar.ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        # Ticks and labels
        ax.set_xticks(range(len(labels)))
        ax.set_yticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha="right")
        ax.set_yticklabels(labels)

        ax.set_title("Tag Pairs")
        ax.set_xlabel("Tag")
        ax.set_ylabel("Tag")

        # Iterate over the lower triangle (and diagonal)
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
        plt.savefig("plots/tag_pairs", dpi=300)
        plt.show()
