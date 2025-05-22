import requests
import os
from dotenv import load_dotenv
from datetime import datetime
import uuid

load_dotenv()

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

def send_to_notion(
    message,
    agent_name=None,
    task_type=None,
    input_text=None,
    output_text=None,
    status="Pending",
    assigned_to=None,
    comment=None,
    pr_url=None,
    conversation_id=None
):
    url = "https://api.notion.com/v1/pages"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }

    # Zajistíme, že conversation_id je vždy nastaven
    if not conversation_id:
        conversation_id = str(uuid.uuid4())

    properties = {
        "Message": {"title": [{"text": {"content": message or "Není zpráva"}}]},  # Opraveno na title
        "Status": {"select": {"name": status or "Pending"}},
        "Timestamp": {"date": {"start": datetime.utcnow().isoformat()}},
        "Agent Name": {"rich_text": [{"text": {"content": agent_name or "Není agent"}}]},
        "Task Type": {"rich_text": [{"text": {"content": task_type or "Není typ úkolu"}}]},
        "Input": {"rich_text": [{"text": {"content": input_text or ""}}]},
        "Output": {"rich_text": [{"text": {"content": output_text or ""}}]},
        "Assigned To": {"people": [] if not assigned_to else [{"id": assigned_to}]} if assigned_to else {"people": []},  # Opraveno na people
        "Comment": {"rich_text": [{"text": {"content": comment or ""}}]},
        "PR URL": {"url": pr_url if pr_url else None},
        "Conversation ID": {"rich_text": [{"text": {"content": conversation_id}}]}
    }

    print(f"Posílám do Notion: {properties}")
    payload = {
        "parent": {"database_id": NOTION_DATABASE_ID},
        "properties": properties
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Odpověď od Notion: Status {response.status_code}, Text: {response.text}")
        if response.status_code != 200:
            raise Exception(f"Chyba při ukládání do Notion: {response.status_code} - {response.text}")
        return response.status_code, response.text
    except Exception as e:
        print(f"Chyba při komunikaci s Notion API: {str(e)}")
        raise