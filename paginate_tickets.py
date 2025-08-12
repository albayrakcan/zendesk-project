import requests
import json
from zendesk_token import load_tokens

tokens = load_tokens()
access_token = tokens["access_token"]

ticket_file = "tickets.json"


def paginate_tickets():
    url = "https://larsa4d.zendesk.com/api/v2/tickets.json?page[size]=100"

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    try:
        with open(ticket_file, "r") as f:
            tickets = json.load(f)
    except FileNotFoundError:
        tickets = []

    while True:
        response = requests.get(url, headers=headers)
        page = response.json()
        ticket_list = page["tickets"]

        for ticket in ticket_list:

            tickets.append({
                "ticket_id": ticket["id"],
                "type": ticket.get("type", None),
                "tags": ticket.get("tags", [])
            })

        save_tickets(tickets)

        # checking if there is any next page. check the syntax
        if not page["meta"]["has_more"]:
            break
        
        # updating the url
        url = page["links"]["next"]

def save_tickets(ticket_data):
    with open(ticket_file, "w") as f:
        json.dump(ticket_data, f, indent=2)

paginate_tickets()
