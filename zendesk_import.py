import requests
import sys
import csv
import time

from zendesk_token import load_tokens
from modules.json_utils import JsonUtils
from modules.ticket_data import TicketData


tokens = load_tokens()
access_token = tokens["access_token"]


def import_all_tickets():
    ticket_file = "data/all_tickets.json"
    csv_file = "data/ticket_list.csv"

    tickets = []

    # Load ticket IDs from CSV
    with open(csv_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        next(reader)  # skip the header row: "Ticket ID"
        for row in reader:

            # Build initial ticket dictionary
            ticket = {
                "id": int(row["Ticket ID"]),
                "date_created": row["Ticket created - Date"],
                "date_solved": row["Ticket solved - Date"],
                "type": row["Ticket type"],
                "tags": [],
            }

            tickets.append(ticket)

    headers = {"Authorization": f"Bearer {access_token}"}

    for ticket in tickets:
        url = "https://larsa4d.zendesk.com/api/v2/tickets/" + str(ticket.get("id"))

        max_retries = 3
        retry_delay = 5  # seconds
        attempt = 0
        success = False

        while attempt < max_retries and not success:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                ticket_data = response.json()["ticket"]

                ticket["tags"] = ticket_data.get("tags", [])

                JsonUtils.save_list_to_json(tickets, ticket_file)
                print(f"✅ Saved ticket {ticket["id"]}")

                success = True  # if we reach here, request was successful

            except requests.exceptions.RequestException as e:
                attempt += 1
                print(
                    f"⚠️ Error fetching ticket {ticket["id"]} (Attempt {attempt}/{max_retries}): {e}"
                )
                if attempt < max_retries:
                    print(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(
                        f"❌ Failed to fetch ticket {ticket["id"]} after {max_retries} attempts."
                    )

    print("✅ Import complete.")


def import_new_tickets():

    ticket_file = "data/all_tickets.json"
    csv_file = "data/ticket_list.csv"
    tickets = TicketData(ticket_file)

    last_ticket_id = tickets.get_last_ticket_id()
    start_appending = False
    new_ticket = {}
    new_tickets = []

    with open(csv_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if start_appending:
                new_ticket = {
                    "id": int(row["Ticket ID"]),
                    "date_created": row["Ticket created - Date"],
                    "date_solved": row["Ticket solved - Date"],
                    "type": row["Ticket type"],
                    "tags": [],
                }
                new_tickets.append(new_ticket)

            elif int(row["Ticket ID"]) == last_ticket_id:
                start_appending = True

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    for ticket in new_tickets:
        url = "https://larsa4d.zendesk.com/api/v2/tickets/" + str(ticket.get("id"))

        max_retries = 3
        retry_delay = 5  # seconds
        attempt = 0
        success = False

        while attempt < max_retries and not success:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                ticket_data = response.json()["ticket"]

                ticket["tags"] = ticket_data.get("tags", [])

                print(f"✅ Saved ticket {ticket["id"]}")

                success = True  # if we reach here, request was successful

            except requests.exceptions.RequestException as e:
                attempt += 1
                print(
                    f"⚠️ Error fetching ticket {ticket["id"]} (Attempt {attempt}/{max_retries}): {e}"
                )
                if attempt < max_retries:
                    print(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(
                        f"❌ Failed to fetch ticket {ticket["id"]} after {max_retries} attempts."
                    )

    JsonUtils.append_list_to_json(new_tickets, ticket_file)
    print("✅ Import complete.")


def import_all_comments():

    ticket_file = "data/all_tickets.json"
    tickets = TicketData(ticket_file)

    headers = {"Authorization": f"Bearer {access_token}"}

    for ticket in tickets:
        ticket["ticket_comments"] = []
        ticket["comment_count"] = None

        url = f"https://larsa4d.zendesk.com/api/v2/tickets/{ticket.get("id")}/comments"

        max_retries = 3
        retry_delay = 5  # seconds
        attempt = 0
        success = False

        while attempt < max_retries and not success:
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()

                comment_data = response.json()["comments"]
                count_data = response.json()["count"]

                ticket["ticket_comments"] = comment_data
                ticket["comment_count"] = int(count_data)

                print(f"✅ Saved ticket comment {ticket["id"]}")
                success = True  # if we reach here, request was successful

            except requests.exceptions.RequestException as e:
                attempt += 1
                print(
                    f"⚠️ Error fetching ticket {ticket["id"]} (Attempt {attempt}/{max_retries}): {e}"
                )
                if attempt < max_retries:
                    print(f"⏳ Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(
                        f"❌ Failed to fetch ticket comment {ticket["id"]} after {max_retries} attempts."
                    )

    print("✅ All comments fetched.")
    tickets.save()


def import_new_comments():
    ticket_file = "data/all_tickets.json"
    csv_file = "data/ticket_list.csv"
    tickets = TicketData(ticket_file)

    last_ticket_id = tickets.get_last_ticket_id()
    start_appending = False
    new_comment = {}
    new_comments = []

    with open(csv_file, "r", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if start_appending:
                new_comment = {

                }
                new_comments.append(new_comment)

            elif int(row["Ticket ID"]) == last_ticket_id:
                start_appending = True






if sys.argv[1] == "import_all_tickets":
    import_all_tickets()
if sys.argv[1] == "import_new_tickets":
    import_new_tickets()
if sys.argv[1] == "import_all_comments":
    import_all_comments()
if sys.argv[1] == "import_new_comments":
    import_new_comments()
