# AutoGen scenario placeholder
from autogen import AssistantAgent, GroupChat, GroupChatManager
from llm_router import route_to_model
import os
from dotenv import load_dotenv

load_dotenv()

config_list = [
    {"model": "gpt-4o", "api_key": os.getenv("OPENAI_API_KEY")},
    {"model": "claude-3-5-sonnet-20240620", "api_key": os.getenv("ANTHROPIC_API_KEY")},
    {"model": "grok-2", "api_key": os.getenv("XAI_API_KEY")}
]

architect = AssistantAgent(
    name="Architect",
    llm_config={"config_list": [config_list[0]]},
    system_message="Navrhuji strukturu a strategii vzdělávací platformy."
)

grok_coder = AssistantAgent(
    name="GrokCoder",
    llm_config={"config_list": [config_list[2]]},
    system_message="Generuji kód s vtipem jako Grok. Kód musí být funkční a dobře okomentovaný."
)

critic = AssistantAgent(
    name="Critic",
    llm_config={"config_list": [config_list[1]]},
    system_message="Kontroluji návrhy a kód, hledám chyby a navrhuji optimalizace."
)

moderator = AssistantAgent(
    name="Moderator",
    llm_config={"config_list": [config_list[0]]},
    system_message="Řídím komunikaci, shromažďuji výstupy a žádám uživatele o schválení."
)

group_chat = GroupChat(
    agents=[architect, grok_coder, critic, moderator],
    messages=[],
    max_round=5
)

manager = GroupChatManager(
    groupchat=group_chat,
    llm_config={"config_list": [config_list[0]]}
)

moderator.initiate_chat(
    manager,
    message="Navrhněte kvízovou komponentu pro vzdělávací platformu. Architect navrhne strukturu (React, Flask, SQLite), GrokCoder vygeneruje kód, Critic zkontroluje kvalitu, Moderator shrne a požádá o schválení."
)