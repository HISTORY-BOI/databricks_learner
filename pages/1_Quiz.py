import random
import streamlit as st
from utils.questions import get_questions, TOPICS

st.set_page_config(page_title="Quiz", page_icon="📝", layout="wide")
st.title("📝 Quiz")


def init_quiz(questions: list[dict]) -> None:
    st.session_state.quiz_questions = questions
    st.session_state.quiz_idx = 0
    st.session_state.quiz_score = 0
    st.session_state.quiz_answered = False
    st.session_state.quiz_selected = None
    st.session_state.quiz_done = False


def render_setup() -> None:
    st.subheader("Quiz konfigurieren")

    topic_options = ["Alle Themen"] + list(TOPICS.keys())
    topic = st.selectbox("Thema", topic_options)

    available = get_questions(topic if topic != "Alle Themen" else None)

    if not available:
        st.warning("Keine Fragen für dieses Thema vorhanden. Füge zuerst Fragen hinzu.")
        return

    max_q = len(available)
    num = st.slider("Anzahl Fragen", min_value=1, max_value=min(max_q, 45), value=min(10, max_q))

    shuffle = st.checkbox("Fragen mischen", value=True)

    st.caption(f"{max_q} Fragen verfügbar für '{topic}'")

    if st.button("▶️ Quiz starten", type="primary"):
        pool = available.copy()
        if shuffle:
            random.shuffle(pool)
        init_quiz(pool[:num])
        st.rerun()


def render_question() -> None:
    questions = st.session_state.quiz_questions
    idx = st.session_state.quiz_idx
    total = len(questions)
    q = questions[idx]

    progress = (idx) / total
    st.progress(progress, text=f"Frage {idx + 1} von {total}  |  Punkte: {st.session_state.quiz_score}")

    st.divider()

    topic_badge = f"`{q.get('topic', '')}` › `{q.get('subtopic', '')}`"
    st.caption(topic_badge)

    st.markdown(f"### {q['question']}")

    if q.get("objective"):
        with st.expander("Lernziel anzeigen"):
            st.write(q["objective"])

    options = q["options"]
    option_labels = [f"**{k}.** {v}" for k, v in options.items()]
    option_keys = list(options.keys())

    if not st.session_state.quiz_answered:
        choice = st.radio(
            "Wähle deine Antwort:",
            option_labels,
            index=None,
            key=f"radio_{idx}",
        )
        if st.button("Antwort bestätigen", disabled=(choice is None), type="primary"):
            selected_idx = option_labels.index(choice)
            st.session_state.quiz_selected = option_keys[selected_idx]
            st.session_state.quiz_answered = True
            if st.session_state.quiz_selected == q["correct_answer"]:
                st.session_state.quiz_score += 1
            st.rerun()
    else:
        selected = st.session_state.quiz_selected
        correct = q["correct_answer"]

        for key, label in zip(option_keys, option_labels):
            if key == correct:
                st.success(f"✅ {label}")
            elif key == selected and selected != correct:
                st.error(f"❌ {label}")
            else:
                st.write(label)

        if selected == correct:
            st.success("**Richtig!**")
        else:
            st.error(f"**Falsch.** Die richtige Antwort ist **{correct}**.")

        if q.get("explanation"):
            with st.expander("Erklärung"):
                st.write(q["explanation"])

        st.divider()
        if idx + 1 < total:
            if st.button("Nächste Frage →", type="primary"):
                st.session_state.quiz_idx += 1
                st.session_state.quiz_answered = False
                st.session_state.quiz_selected = None
                st.rerun()
        else:
            if st.button("Ergebnis anzeigen", type="primary"):
                st.session_state.quiz_done = True
                st.rerun()


def render_result() -> None:
    score = st.session_state.quiz_score
    total = len(st.session_state.quiz_questions)
    pct = score / total * 100

    st.subheader("Quiz abgeschlossen!")

    if pct >= 80:
        st.balloons()
        st.success(f"### {score} / {total} — {pct:.0f}% 🎉 Sehr gut!")
    elif pct >= 60:
        st.info(f"### {score} / {total} — {pct:.0f}% 👍 Gut, aber noch Luft nach oben.")
    else:
        st.warning(f"### {score} / {total} — {pct:.0f}% 📚 Mehr Übung empfohlen.")

    st.caption("Zum Bestehen der Prüfung sind typischerweise ~70% erforderlich.")

    if st.button("Neues Quiz starten", type="primary"):
        for key in ["quiz_questions", "quiz_idx", "quiz_score", "quiz_answered", "quiz_selected", "quiz_done"]:
            st.session_state.pop(key, None)
        st.rerun()


if "quiz_questions" not in st.session_state:
    render_setup()
elif st.session_state.get("quiz_done"):
    render_result()
else:
    render_question()
