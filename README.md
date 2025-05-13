# AI Collaboration Hub
AI Collaboration Hub
Tento projekt je pokročilý nástroj pro spolupráci s umělou inteligencí, který využívá různé jazykové modely (OpenAI, Anthropic, xAI) k řešení úkolů jako návrh strategií, generování kódu, kontrola kvality a podrobné analýzy. Systém je postaven na FastAPI backendu, Streamlit GUI a integraci s Notion pro ukládání výsledků.
Co jsme stvořili

Multi-agentní systém: Čtyři agenti (Architect, Coder, Critic, GrokCoder) a jeden analytický agent (GrokAnalyst) spolupracují na různých úkolech.
Podporované modely:
OpenAI GPT-4o pro strategie.
Anthropic Claude-3-5-Sonnet-20240620 pro kontrolu a vylepšení.
xAI Grok-2 pro vtipné generování kódu.
xAI Grok-3-beta pro pokročilé analýzy.


Funkce:
Zpracování úkolů (strategie, kritika, grok_kód, grok_3_analýza).
Ukládání výsledků do Notion databáze.
Robustní zpracování s retry a delšími timeouty pro pomalé odpovědi.


Technologie: Python, FastAPI, Streamlit, httpx, Notion API.

Jak to funguje
Systém běží na lokálním serveru s FastAPI, který komunikuje s API různých modelů. Streamlit poskytuje jednoduché grafické rozhraní, kde zadáš úkol a vybereš typ (strategie, kritika, atd.). Výsledky se ukládají do Notion databáze pro pozdější přezkoumání.
Instalace

Klonuj repozitář:git clone https://github.com/VikitorFree/ai-collaboration-hub.git
cd ai-collaboration-hub


Vytvoř virtuální prostředí:python -m venv venv-agent
python -m venv venv-gui


Nainstaluj závislosti:.\venv-agent\Scripts\activate
pip install fastapi uvicorn httpx tenacity python-dotenv
.\venv-gui\Scripts\activate
pip install streamlit requests


Nastav proměnné prostředí:
Vytvoř .env soubor v kořenovém adresáři a přidej:
OPENAI_API_KEY=tvůj_API_klíč
XAI_API_KEY=tvůj_API_klíč
ANTHROPIC_API_KEY=tvůj_API_klíč
NOTION_API_KEY=tvůj_API_klíč
NOTION_DATABASE_ID=tvé_database_id




Spusť server a GUI:
FastAPI:.\venv-agent\Scripts\activate
uvicorn main:app --reload


Streamlit:.\venv-gui\Scripts\activate
streamlit run frontend/app.py





Použití

Otevři Streamlit GUI v prohlížeči (obvykle http://localhost:8501).
Vyber typ úkolu (strategie, kritika, grok_kód, grok_3_analýza).
Zadej obsah úkolu (např. „Vytvoř 5 otázek pro kvíz“).
Klikni na „Odeslat“ a počkej na výsledek.
Výsledky se uloží do Notion databáze (zkontroluj pod ID uvedeným v .env).

Technické detaily

Timeout: Systém zvládá pomalé odpovědi (např. Grok-3-beta) díky timeoutu 120 sekund v GUI a 60 sekund na serveru.
Retry: Automatické opakování při síťových chybách (3 pokusy s 2sekundovým čekáním).
Logování: Chyby a úspěchy jsou zaznamenávány v router.log.

Příspěvky

Projekt je otevřený pro příspěvky! Pokud chceš přidat nové agenty, modely nebo funkce, vytvoř pull request.
Nahlas chyby na GitHub Issues.

Licence
MIT License – Ujisti se, že máš licenci v repozitáři.
Happy coding a ať se daří s tvým AI hubem!
