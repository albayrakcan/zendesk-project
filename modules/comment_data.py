import json
import os

from modules.json_utils import JsonUtils

class CommentData:
    
    def __init__(self, file_path):
        self.file_path = file_path
        self.comments = self.load_comments()

    def load_comments(self):
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"{self.file_path} not found.")
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)
        
    def save(self):
        JsonUtils.save_list_to_json(self.comments, self.file_path)
        print(f"✅ Comments saved to {self.file_path}")
        
    def get_comments(self):
        return self.comments.get("comments", [])
    
    def organize_comments(self, agent_ids_file):
        agent_ids_dict = JsonUtils.load_json(agent_ids_file)
        agent_ids = [id_values for dict in agent_ids_dict for id_values in dict.values()]

        comment_list = self.comments.get_comments()
        replies = []
        for comment in comment_list:
            reply = {
                "role": "agent" if comment.get("author_id") in agent_ids else "user",
                "visibility": "public" if comment.get("public") == True else "private",
                "message": comment.get("plain_body")
            }
            replies.append(reply)
        target_path = ...
        JsonUtils.save_list_to_json(replies,target_path)
        print(f"✅ Comments are organized and saved to {target_path}")

    


