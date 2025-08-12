import requests
import sys
import csv
import time

from zendesk_token import load_tokens
from modules.json_utils import JsonUtils
from modules.ticket_data import TicketData


ticket_file = "data/all_tickets.json"
csv_file = "data/ticket_list.csv"
tickets = TicketData(ticket_file)

last_ticket_id = tickets.get_last_ticket_id()
start_appending = False
new_tickets = []
new_ticket = {}

with open(csv_file, "r", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:

        if start_appending:
            new_ticket = {
                "id": row["Ticket ID"],
                "date_created": row["Ticket created - Date"],
                "date_solved": row["Ticket solved - Date"],
                "type": row["Ticket type"],
                "tags": []
            }

            new_tickets.append(new_ticket)

        elif int(row["Ticket ID"]) == last_ticket_id:
            start_appending = True


