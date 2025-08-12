import sys

from modules.ticket_data import TicketData
from modules.json_utils import JsonUtils




ticket_file = "D:/Desktop/larsa_AI_project/zendesk/data/all_tickets.json"
tag_file = "D:/Desktop/larsa_AI_project/zendesk/data/all_tags.json"
output_base = "D:/Desktop/larsa_AI_project/zendesk/ticket_comments"
ignored_tags_file = "D:/Desktop/larsa_AI_project/zendesk/data/ignored_tags.json"

ignored_tags = JsonUtils.load_json(ignored_tags_file)

tickets = TicketData(ticket_file)


if sys.argv[1] == "clean_tags":
    tickets.clean_tags()

if sys.argv[1] == "sanitize_tags":
    tickets.sanitize_tags()

elif sys.argv[1] == "seperate_version_tags":
    tickets.seperate_version_tags()

elif sys.argv[1] == "get_tags":
    tickets.get_tags(tag_file)

elif sys.argv[1] == "create_folders":
    tickets.create_tag_subfolders(output_base, ignore_tags=ignored_tags)