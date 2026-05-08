import streamlit as st
from utils.questions import add_question, delete_question, get_questions, TOPICS

st.set_page_config(page_title="Fragen hinzufügen", page_icon="➕", layout="wide")
st.title("➕ Frage manuell hinzufügen")

tab_add, tab_view = st.tabs(["Neue Frage", "Fragenbank"])

with tab_add:
    with st.form("add_question_form", clear_on_submit=True):
        topic = st.selectbox("Thema *", list(TOPICS.keys()))
        subtopic = st.selectbox("Unterthema *", TOPICS[topic])
        objective = st.text_area("Lernziel (aus dem Exam Guide)", height=60)
        question = st.text_area("Frage *", height=100)

        st.markdown("**Antwortoptionen** (A–D)")
        col1, col2 = st.columns(2)
        with col1:
            opt_a = st.text_area("A", height=80, key="opt_a")
            opt_b = st.text_area("B", height=80, key="opt_b")
        with col2:
            opt_c = st.text_area("C", height=80, key="opt_c")
            opt_d = st.text_area("D", height=80, key="opt_d")

        correct = st.radio("Richtige Antwort *", ["A", "B", "C", "D"], horizontal=True)
        explanation = st.text_area("Erklärung (wird nach der Antwort gezeigt)", height=100)

        submitted = st.form_submit_button("Frage speichern", type="primary")

    if submitted:
        if not question.strip() or not all([opt_a, opt_b, opt_c, opt_d]):
            st.error("Bitte Frage und alle vier Antwortoptionen ausfüllen.")
        else:
            add_question({
                "topic": topic,
                "subtopic": subtopic,
                "objective": objective.strip(),
                "question": question.strip(),
                "options": {
                    "A": opt_a.strip(),
                    "B": opt_b.strip(),
                    "C": opt_c.strip(),
                    "D": opt_d.strip(),
                },
                "correct_answer": correct,
                "explanation": explanation.strip(),
                "source": "manual",
            })
            st.success("Frage gespeichert!")

with tab_view:
    topic_filter = st.selectbox(
        "Filtern nach Thema",
        ["Alle Themen"] + list(TOPICS.keys()),
        key="view_filter",
    )
    questions = get_questions(topic_filter if topic_filter != "Alle Themen" else None)

    if not questions:
        st.info("Keine Fragen vorhanden.")
    else:
        st.caption(f"{len(questions)} Frage(n) gefunden")
        for q in questions:
            with st.expander(f"[{q.get('topic', '')}] {q['question'][:80]}…"):
                st.markdown(f"**Thema:** {q.get('topic')} › {q.get('subtopic')}")
                if q.get("objective"):
                    st.markdown(f"**Lernziel:** {q['objective']}")
                st.markdown("**Optionen:**")
                for key, val in q["options"].items():
                    marker = "✅" if key == q["correct_answer"] else "  "
                    st.markdown(f"{marker} **{key}.** {val}")
                if q.get("explanation"):
                    st.markdown(f"**Erklärung:** {q['explanation']}")
                st.caption(f"Quelle: {q.get('source', '—')}  |  Erstellt: {q.get('created_at', '—')}")
                if st.button("🗑️ Löschen", key=f"del_{q['id']}"):
                    delete_question(q["id"])
                    st.success("Frage gelöscht.")
                    st.rerun()
