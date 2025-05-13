# FastAPI orchestrator placeholder
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import requests
import logging
from llm_router import route_to_model

# Nastavení logování
logging.basicConfig(level=logging.INFO, filename='app.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Načtení proměnných prostředí
load_dotenv()
NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_DATABASE_ID = os.getenv("NOTION_DATABASE_ID")

# Inicializace FastAPI
app = FastAPI(title="AI Collaboration Hub")

# Model pro příchozí požadavky
class TaskRequest(BaseModel):
    task_type: str
    content: str

# Funkce pro odeslání notifikace do Notion
def notify_notion(message: str, pr_url: str = None) -> bool:
    """
    Odesílá notifikaci do Notion databáze pro human-in-the-loop schvalování.
    """
    try:
        payload = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "Message": {"title": [{"text": {"content": message}}]},
                "PR URL": {"url": pr_url if pr_url else None},
                "Status": {"select": {"name": "Pending"}}
            }
        }
        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"
        }
        response = requests.post("https://api.notion.com/v1/pages", json=payload, headers=headers)
        if response.status_code == 200:
            logger.info(f"Notifikace odeslána do Notion: {message}")
            return True
        else:
            logger.error(f"Chyba při odesílání do Notion: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Výjimka při odesílání do Notion: {str(e)}")
        return False

# HTTP endpoint pro zpracování úkolů
@app.post("/process_task")
async def process_task(request: TaskRequest):
    """
    Zpracovává úkoly přijaté z GUI a odesílá notifikaci do Notion.
    """
    try:
        logger.info(f"Přijat úkol: {request.task_type}, obsah: {request.content[:50]}...")
        # Volání routeru pro směrování k agentovi (GPT-4, Claude, Grok 2)
        response = await route_to_model(request.task_type, request.content)
        
        # Odeslání notifikace do Notion
        notion_message = f"Úkol dokončen ({request.task_type}): {request.content[:100]}..."
        notify_notion(notion_message)
        
        return {"response": response}
    except Exception as e:
        logger.error(f"Chyba při zpracování úkolu: {str(e)}")
        return {"error": f"Chyba při zpracování úkolu: {str(e)}"}

# WebSocket endpoint pro real-time aktualizace
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    Zajišťuje real-time komunikaci mezi GUI a serverem.
    """
    await websocket.accept()
    try:
        while True:
            # Přijetí dat z GUI
            data = await websocket.receive_json()
            task_type = data.get("task_type")
            content = data.get("content")
            
            logger.info(f"WebSocket: Přijat úkol: {task_type}, obsah: {content[:50]}...")
            
            # Volání routeru pro směrování k agentovi
            response = await route_to_model(task_type, content)
            
            # Odeslání notifikace do Notion
            notion_message = f"Real-time úkol dokončen ({task_type}): {content[:100]}..."
            notify_notion(notion_message)
            
            # Odeslání odpovědi zpět do GUI
            await websocket.send_json({
                "task_type": task_type,
                "response": response,
                "status": "success"
            })
    except WebSocketDisconnect:
        logger.info("WebSocket odpojen")
    except Exception as e:
        logger.error(f"Chyba v WebSocketu: {str(e)}")
        await websocket.send_json({
            "task_type": task_type,
            "response": f"Chyba: {str(e)}",
            "status": "error"
        })
        await websocket.close()

# Spuštění serveru (pro ladění)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)