import json
import os
import streamlit as st
import anthropic
from utils.questions import add_questions_bulk, TOPICS

st.set_page_config(page_title="KI-Generator", page_icon="🤖", layout="wide")
st.title("🤖 KI-Fragen generieren")
st.caption("Generiert Prüfungsfragen mit Claude basierend auf den offiziellen Exam-Themen.")

SYSTEM_PROMPT = """Du bist ein Experte für die Databricks Certified Data Engineer Associate Prüfung (Version ab Mai 2026).
Generiere realistische Multiple-Choice-Prüfungsfragen im exakten Stil der Databricks-Zertifizierungsprüfung.

Regeln:
- Jede Frage hat genau 4 Optionen (A, B, C, D)
- Nur eine Antwort ist korrekt
- Alle falschen Antworten (Distraktoren) müssen plausibel klingen
- Fragen sollen praktische Szenarien beschreiben, nicht nur theoretisches Wissen abfragen
- Die Erklärung soll erklären warum die richtige Antwort richtig ist UND warum die anderen falsch sind
- Fragen auf Englisch (so wie in der echten Prüfung)

Gib die Antwort AUSSCHLIESSLICH als gültiges JSON-Array zurück, ohne Markdown-Code-Blöcke oder Erklärungstext davor/danach.

Format:
[
  {
    "question": "...",
    "options": {"A": "...", "B": "...", "C": "...", "D": "..."},
    "correct_answer": "A",
    "explanation": "..."
  }
]"""


def get_api_key() -> str | None:
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if key:
        return key
    st.warning("Kein ANTHROPIC_API_KEY als Umgebungsvariable gefunden.")
    entered = st.text_input("API-Schlüssel eingeben:", type="password", key="api_key_input")
    return entered or None


def generate_questions(api_key: str, topic: str, subtopic: str, num: int, extra: str) -> list[dict]:
    client = anthropic.Anthropic(api_key=api_key)

    user_prompt = f"""Generiere {num} Prüfungsfrage(n) für die Databricks Data Engineer Associate Prüfung.

Thema: {topic}
Unterthema: {subtopic}
{"Zusätzliche Anforderungen: " + extra if extra.strip() else ""}

Antworte ausschließlich mit dem JSON-Array."""

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


api_key = get_api_key()

st.divider()

col1, col2 = st.columns([2, 1])
with col1:
    topic = st.selectbox("Thema", list(TOPICS.keys()))
with col2:
    subtopic = st.selectbox("Unterthema", TOPICS[topic])

num_questions = st.slider("Anzahl zu generierender Fragen", min_value=1, max_value=10, value=3)
extra_context = st.text_area(
    "Zusätzlicher Kontext (optional)",
    placeholder="z. B. 'Fokus auf streaming mode' oder 'Schwierigkeit: fortgeschritten'",
    height=80,
)

if "generated_questions" not in st.session_state:
    st.session_state.generated_questions = []

generate_clicked = st.button(
    "🤖 Fragen generieren",
    type="primary",
    disabled=(not api_key),
)

if generate_clicked and api_key:
    with st.spinner(f"Generiere {num_questions} Frage(n) für '{subtopic}'…"):
        try:
            generated = generate_questions(api_key, topic, subtopic, num_questions, extra_context)
            for q in generated:
                q["topic"] = topic
                q["subtopic"] = subtopic
                q["source"] = "ai"
                q["objective"] = subtopic
            st.session_state.generated_questions = generated
            st.success(f"{len(generated)} Frage(n) generiert. Überprüfe und speichere sie unten.")
        except json.JSONDecodeError as e:
            st.error(f"KI-Antwort konnte nicht als JSON geparst werden: {e}")
        except anthropic.APIError as e:
            st.error(f"API-Fehler: {e}")

if st.session_state.generated_questions:
    st.divider()
    st.subheader("Generierte Fragen — Review")

    approved_ids = []
    for i, q in enumerate(st.session_state.generated_questions):
        with st.expander(f"Frage {i + 1}: {q['question'][:70]}…", expanded=True):
            approved = st.checkbox("Frage übernehmen", value=True, key=f"approve_{i}")
            if approved:
                approved_ids.append(i)

            edited_question = st.text_area("Fragetext", value=q["question"], key=f"q_text_{i}", height=80)
            q["question"] = edited_question

            cols = st.columns(2)
            for j, (key, val) in enumerate(q["options"].items()):
                with cols[j % 2]:
                    new_val = st.text_area(f"Option {key}", value=val, key=f"opt_{i}_{key}", height=70)
                    q["options"][key] = new_val

            correct = st.radio(
                "Richtige Antwort",
                list(q["options"].keys()),
                index=list(q["options"].keys()).index(q["correct_answer"]),
                horizontal=True,
                key=f"correct_{i}",
            )
            q["correct_answer"] = correct

            new_expl = st.text_area("Erklärung", value=q.get("explanation", ""), key=f"expl_{i}", height=100)
            q["explanation"] = new_expl

    st.divider()
    save_col, discard_col = st.columns([1, 3])
    with save_col:
        if st.button("✅ Ausgewählte speichern", type="primary"):
            to_save = [st.session_state.generated_questions[i] for i in approved_ids]
            if to_save:
                count = add_questions_bulk(to_save)
                st.success(f"{count} Frage(n) gespeichert!")
                st.session_state.generated_questions = []
                st.rerun()
            else:
                st.warning("Keine Fragen zum Speichern ausgewählt.")
    with discard_col:
        if st.button("🗑️ Verwerfen"):
            st.session_state.generated_questions = []
            st.rerun()
