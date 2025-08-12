import requests
import json
from zendesk_token import load_tokens

tokens = load_tokens()
access_token = tokens["access_token"]

ticket_id = 10
url = f"https://larsa4d.zendesk.com/api/v2/tickets/{ticket_id}"
email_address = "calbayrak@larsa4d.com"

headers = {
    'Authorization': f'Bearer {access_token}',
}

response = requests.get(url, headers=headers)
print(response.json())