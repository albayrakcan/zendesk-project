import requests
import json
import sys

from zendesk_token import load_tokens
from modules.json_utils import JsonUtils
from modules.comment_data import CommentData


def get_comments(ticket_id):
    
    tokens = load_tokens()
    access_token = tokens["access_token"]

    url = f"https://larsa4d.zendesk.com/api/v2/tickets/{ticket_id}/comments"
    email_address = "calbayrak@larsa4d.com"

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    response = requests.get(url, headers=headers)
    comment = response.json()
    JsonUtils.save_list_to_json(comment, "data/test_comment.json")

def test_organize_comment():
    agent_ids_file = "data/agent_ids.json"
    comment_file = "data/test_comment.json"

    agent_ids_dict = JsonUtils.load_json(agent_ids_file)
    agent_ids = [id_values for dict in agent_ids_dict for id_values in dict.values()]
    comment = CommentData(comment_file)

    comment_list = comment.get_comments()
    replies = []

    for comment in comment_list:
        reply = {
            "role": "agent" if comment.get("author_id") in agent_ids else "user",
            "visibility": "public" if comment.get("public") == True else "private",
            "message": comment.get("plain_body")
        }
        replies.append(reply)
    test_file = "data/test_file.json"
    JsonUtils.save_list_to_json(replies,test_file)







if len(sys.argv) == 2:
      get_comments(sys.argv[1])
else:
     test_organize_comment()



