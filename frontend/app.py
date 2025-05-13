import streamlit as st
import requests
from graphviz import Digraph

st.title("AI Collaboration Hub")

# Vizuální mapa agentů
st.subheader("Stav agentů")
dot = Digraph()
dot.node("Architect", "Architect (GPT-4)")
dot.node("GrokCoder", "GrokCoder (Grok 2)")
dot.node("Grok3", "Grok3 (Grok 3 beta)")
dot.node("Critic", "Critic (Claude)")
dot.node("Moderator", "Moderator (GPT-4)")
dot.edges([
    ("Architect", "GrokCoder"),
    ("GrokCoder", "Grok3"),
    ("Grok3", "Critic"),
    ("Critic", "Moderator")
])
st.graphviz_chart(dot)

# Zadání úkolu
task_type = st.selectbox("Vyber typ úkolu", ["strategie", "kritika", "grok_kód", "grok_3_analýza"])
content = st.text_area("Zadej úkol")
if st.button("Odeslat"):
    try:
        response = requests.post(
            "http://localhost:8000/process_task",
            json={"task_type": task_type, "content": content},
            timeout=120
        )
        response.raise_for_status()
        st.write(response.json()["response"])
    except Exception as e:
        st.error(f"Chyba: {str(e)}")