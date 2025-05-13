import httpx
import os
from dotenv import load_dotenv
import logging
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type

# Nastavení logování
logging.basicConfig(level=logging.INFO, filename='router.log', format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Načtení proměnných prostředí
load_dotenv()

# API klíče a hlavičky
gpt_api_key = os.getenv("OPENAI_API_KEY")
grok_api_key = os.getenv("XAI_API_KEY")
claude_api_key = os.getenv("ANTHROPIC_API_KEY")

headers_gpt = {
    "Authorization": f"Bearer {gpt_api_key}",
    "Content-Type": "application/json"
}

headers_grok = {
    "Authorization": f"Bearer {grok_api_key}",
    "Content-Type": "application/json"
}

headers_claude = {
    "x-api-key": claude_api_key,
    "anthropic-version": "2023-06-01",
    "Content-Type": "application/json"
}

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type((httpx.ReadTimeout, httpx.RemoteProtocolError)),
    reraise=True
)
async def call_gpt(prompt: str):
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            logger.info(f"Volání GPT-4o s payload: {payload}")
            response = await client.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers_gpt,
                json=payload
            )
            logger.info(f"GPT-4o odpověď: status={response.status_code}, text={response.text[:200]}...")
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP chyba při volání GPT-4o: status={e.response.status_code}, text={e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Obecná chyba při volání GPT-4o: {str(e)}, typ={type(e).__name__}")
            raise

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type((httpx.ReadTimeout, httpx.RemoteProtocolError)),
    reraise=True
)
async def call_grok(prompt: str, model: str, system_prompt: str = ""):
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 1500
    }
    async with httpx.AsyncClient(timeout=60.0) as client:  # Zvýšení timeoutu na 60s pro grok-3-beta
        try:
            logger.info(f"Volání Grok ({model}) s payload: {payload}")
            response = await client.post(
                "https://api.x.ai/v1/chat/completions",
                headers=headers_grok,
                json=payload
            )
            logger.info(f"Grok ({model}) odpověď: status={response.status_code}, text={response.text[:200]}...")
            response.raise_for_status()
            return response.json()["choices"][0]["message"]["content"]
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP chyba při volání Grok ({model}): status={e.response.status_code}, text={e.response.text}")
            raise
        except Exception as e:
            logger.error(f"Obecná chyba při volání Grok ({model}): {str(e)}, typ={type(e).__name__}")
            raise

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    retry=retry_if_exception_type((httpx.ReadTimeout, httpx.RemoteProtocolError)),
    reraise=True
)
async def call_claude(prompt: str):
    models = ["claude-3-5-sonnet-20240620", "claude-3-sonnet-20240229"]  # Seznam modelů k vyzkoušení
    for model in models:
        payload = {
            "model": model,
            "max_tokens": 500,
            "temperature": 0.7,
            "messages": [{"role": "user", "content": prompt}]
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                logger.info(f"Volání Claude s payload: {payload}")
                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers_claude,
                    json=payload
                )
                logger.info(f"Claude odpověď: status={response.status_code}, text={response.text[:200]}...")
                response.raise_for_status()
                return response.json()["content"][0]["text"]
            except httpx.HTTPStatusError as e:
                logger.error(f"HTTP chyba při volání Claude ({model}): status={e.response.status_code}, text={e.response.text}")
                if e.response.status_code == 404:
                    logger.warning(f"Model {model} nenalezen, zkouším další...")
                    continue
                raise
            except Exception as e:
                logger.error(f"Obecná chyba při volání Claude ({model}): {str(e)}, typ={type(e).__name__}")
                raise
    raise Exception("Žádný podporovaný model Claude nenalezen.")

async def route_to_model(task_type: str, content: str):
    try:
        logger.info(f"Zpracovávám úkol: {task_type}, obsah: {content[:50]}...")
        if task_type == "strategie":
            return await call_gpt(content)
        elif task_type == "kritika":
            return await call_claude(content)
        elif task_type == "grok_kód":
            return await call_grok(
                content,
                model="grok-2",
                system_prompt="You are Grok, a snarky and witty AI by xAI. Provide concise, practical code solutions with a touch of humor."
            )
        elif task_type == "grok_3_analýza":
            return await call_grok(
                content,
                model="grok-3-beta",
                system_prompt="You are Grok 3, an advanced AI by xAI with PhD-level expertise in analysis and reasoning. Provide detailed, accurate, and insightful responses."
            )
        else:
            logger.warning(f"Neznámý typ úkolu: {task_type}")
            return "Neznámý typ úkol"
    except Exception as e:
        logger.error(f"Chyba při směrování modelu: {str(e)}, typ={type(e).__name__}")
        return f"Chyba při volání modelu: {str(e)}"