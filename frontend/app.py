import streamlit as st
import asyncio
from datetime import datetime
from graphviz import Digraph
import sys
import os
import uuid

# Přidání kořenového adresáře do sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fetch_notion_history import fetch_notion_history
from integrations.notify_notion import send_to_notion
from llm_router import route_to_model

# Nastavení širokého layoutu
st.set_page_config(layout="wide")

# CSS pro odstranění okrajů a maximální šířku
st.markdown(
    """
    <style>
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("AI Collaboration Hub")

# Rozdělení na sloupce s větším prostorem pro historii
col1, col2 = st.columns([1, 4])

# Inicializace stavu pro vlákno
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "history" not in st.session_state:
    st.session_state.history = []

# Načtení historie z Notion při startu
with col1:
    st.subheader("Správa vlákna")
    if st.button("Nové vlákno"):
        st.session_state.conversation_id = str(uuid.uuid4())
        st.session_state.history = []
    conversation_id_display = st.session_state.conversation_id or "Žádné vlákno"
    st.write(f"Aktuální vlákno: {conversation_id_display}")

    # Načtení historie podle conversation_id
    try:
        st.session_state.history = fetch_notion_history(st.session_state.conversation_id)
    except Exception as e:
        st.warning(f"Chyba při načítání historie z Notion: {e}")
        st.session_state.history = []

# Vizuální mapa agentů
with col1:
    st.subheader("Stav agentů")
    dot = Digraph()
    dot.node("Architect", "Architect (GPT-4)")
    dot.node("GrokCoder", "GrokCoder (Grok 2)")
    dot.node("GrokAnalyst", "GrokAnalyst (Grok 3 beta)")
    dot.node("Critic", "Critic (Claude)")
    dot.edges([
        ("Architect", "GrokCoder"),
        ("GrokCoder", "GrokAnalyst"),
        ("GrokAnalyst", "Critic")
    ])
    st.graphviz_chart(dot, use_container_width=True)

# Definice workflow
workflow = [
    ("Architect", "strategie"),
    ("GrokCoder", "grok_kód"),
    ("Critic", "kritika")
]

# Zadání úkolu
with col1:
    st.subheader("Zadej úkol")
    agent_type = st.selectbox("Zvol agenta", [
        "Architect",
        "Coder",
        "Critic",
        "GrokCoder",
        "GrokAnalyst"
    ])

    task_mapping = {
        "Architect": "strategie",
        "Coder": "grok_kód",
        "Critic": "kritika",
        "GrokCoder": "grok_kód",
        "GrokAnalyst": "grok_3_analýza"
    }

    task_type = task_mapping[agent_type]
    user_input = st.text_area("Zadej zprávu", height=200)
    uploaded_file = st.file_uploader("Nahraj soubor (volitelné)", type=["txt", "pdf", "png", "jpg"])
    auto_process = st.checkbox("Automatické zpracování (Architect → GrokCoder → Critic)")

    if st.button("Odeslat"):
        with st.spinner("Zpracovávám..."):
            try:
                # Zajistíme, že conversation_id je nastaven
                if not st.session_state.conversation_id:
                    st.session_state.conversation_id = str(uuid.uuid4())

                # Zpracování nahraného souboru
                file_content = ""
                if uploaded_file:
                    if uploaded_file.type.startswith("text"):
                        file_content = uploaded_file.read().decode("utf-8")
                    elif uploaded_file.type in ["application/pdf", "image/png", "image/jpeg"]:
                        file_content = f"[Soubor: {uploaded_file.name} – obsah není přímo čitelný, nahrajte jako text nebo popište.]"
                    user_input = f"{user_input}\n\nPříloha:\n{file_content}" if file_content else user_input

                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

                # Pokud je vybráno automatické zpracování, projdeme workflow
                if auto_process:
                    current_input = user_input
                    for agent, task in workflow:
                        context = "\n".join(
                            f"{item['agent']}: {item['input']} -> {item['response']}"
                            for item in st.session_state.history[-3:]
                        )
                        full_input = f"Kontext:\n{context}\n\nNový úkol:\n{current_input}" if context else current_input

                        response = loop.run_until_complete(
                            asyncio.wait_for(route_to_model(task, full_input), timeout=300)
                        )
                        entry = {
                            "agent": agent,
                            "task_type": task,
                            "input": current_input,
                            "response": response,
                            "timestamp": datetime.now().strftime("%H:%M:%S %d.%m.%Y"),
                            "conversation_id": st.session_state.conversation_id
                        }
                        st.session_state.history.append(entry)

                        send_to_notion(
                            message=f"Úkol dokončen ({task}): {current_input[:50]}...",
                            agent_name=agent,
                            task_type=task,
                            input_text=current_input,
                            output_text=response,
                            status="Completed",
                            conversation_id=st.session_state.conversation_id,
                            comment=f"Soubor: {uploaded_file.name}" if uploaded_file else None
                        )
                        current_input = response  # Předat odpověď dalšímu agentovi
                else:
                    # Normální zpracování jedním agentem
                    context = "\n".join(
                        f"{item['agent']}: {item['input']} -> {item['response']}"
                        for item in st.session_state.history[-3:]
                    )
                    full_input = f"Kontext:\n{context}\n\nNový úkol:\n{user_input}" if context else user_input

                    response = loop.run_until_complete(
                        asyncio.wait_for(route_to_model(task_type, full_input), timeout=300)
                    )
                    entry = {
                        "agent": agent_type,
                        "task_type": task_type,
                        "input": user_input,
                        "response": response,
                        "timestamp": datetime.now().strftime("%H:%M:%S %d.%m.%Y"),
                        "conversation_id": st.session_state.conversation_id
                    }
                    st.session_state.history.append(entry)

                    send_to_notion(
                        message=f"Úkol dokončen ({task_type}): {user_input[:50]}...",
                        agent_name=agent_type,
                        task_type=task_type,
                        input_text=user_input,
                        output_text=response,
                        status="Completed",
                        conversation_id=st.session_state.conversation_id,
                        comment=f"Soubor: {uploaded_file.name}" if uploaded_file else None
                    )

            except asyncio.TimeoutError:
                st.error("Časový limit vypršel – zkus úkol zjednodušit nebo kontaktuj podporu.")
            except Exception as e:
                st.error(f"Chyba: {str(e)}")

# Zobrazení historie
with col2:
    st.subheader("Historie odpovědí")
    if st.session_state.history:
        for item in reversed(st.session_state.history):
            with st.expander(f"{item['agent']} ({item['task_type']}) – {item['input'][:40]}..."):
                st.markdown(f"**Vstup:** {item['input']}")
                st.markdown(f"**Odpověď:** {item['response']}")
                st.markdown(f"**Čas:** {item['timestamp']}")
    else:
        st.info("Zatím žádná historie.")