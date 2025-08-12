from modules.data_analysis import DataAnalysis
from modules.ticket_data import TicketData
from modules.json_utils import JsonUtils
import sys


ticket_file = "data/all_tickets.json"
tag_csv_file = "data/tag_counts.csv"
ignored_tags_file = "data/ignored_tags.json"

tickets = TicketData(ticket_file)
ignored_tags = set(JsonUtils.load_json(ignored_tags_file))
tag_counter = tickets.count_tags(csv_file=tag_csv_file, ignored_tags=ignored_tags)

if sys.argv[1] == "top_tags":
    DataAnalysis.tags_by_freq(tag_counter, 20)

if sys.argv[1] == "tag_freq":
    tags = [tag for tag, _ in tag_counter.most_common(10)]

    index, series = tickets.get_yearly_tag_counts(tags, start_year=2019)
    DataAnalysis.tag_trends_line(index, series, str_type="year")

    # index, series = tickets.get_monthly_tag_counts(tags, months=5)
    # DataAnalysis.tag_trends_line(index, series, str_type="month")

if sys.argv[1] == "tag_pairs":
    tags = [tag for tag, _ in tag_counter.most_common(10)]
    matrix, labels = tickets.build_cooccurrence(tags, ignored_tags=None)
    DataAnalysis.plot_cooccurrence_heatmap(matrix,labels)


