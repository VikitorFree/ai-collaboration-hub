import requests
import os
from dotenv import load_dotenv

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def send_to_notion(message, pr_url=None, status="Pending"):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": {
            "Message": {"title": [{"text": {"content": message}}]},
            "PR URL": {"url": pr_url} if pr_url else {},
            "Status": {"select": {"name": status}}
        }
    }

    response = requests.post(url, headers=headers, json=payload)
    return response.status_code, response.text
