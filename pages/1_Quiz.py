import random
from pathlib import Path
import streamlit as st
from utils.questions import get_questions, TOPICS

st.set_page_config(page_title="Quiz", page_icon="📝", layout="wide")
st.title("📝 Quiz")


def render_markdown(text: str, prefix: str = "") -> None:
    """Render text preserving newlines as visible line breaks; HTML passes through."""
    body = text.replace("\n", "  \n")
    st.markdown(prefix + body, unsafe_allow_html=True)


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

    render_markdown(q["question"], prefix="### ")

    for img_path in q.get("images", []):
        if Path(img_path).exists():
            st.image(img_path)

    if q.get("objective"):
        with st.expander("Lernziel anzeigen"):
            st.write(q["objective"])

    options = q["options"]
    option_images = q.get("option_images", {})
    option_keys = list(options.keys())
    correct = q["correct_answer"]
    is_multi = len(correct) > 1

    def render_option_body(key: str, value: str) -> None:
        """Renders the content of one option: image (if any) + text (if any)."""
        img = option_images.get(key)
        if img and Path(img).exists():
            st.image(img, use_container_width=True)
        if value:
            render_markdown(value)

    st.divider()

    if not st.session_state.quiz_answered:
        if is_multi:
            st.caption(f"**Mehrfachauswahl** — {len(correct)} Antworten richtig")
            selected: list[str] = []
            for k, v in options.items():
                checkbox_col, content_col = st.columns([1, 12])
                with checkbox_col:
                    checked = st.checkbox(f"**{k}**", key=f"cb_{idx}_{k}", label_visibility="visible")
                    if checked:
                        selected.append(k)
                with content_col:
                    render_option_body(k, v)
                st.divider()
            confirm_disabled = len(selected) == 0
            if st.button("Antwort bestätigen", disabled=confirm_disabled, type="primary"):
                st.session_state.quiz_selected = "".join(sorted(selected))
                st.session_state.quiz_answered = True
                if st.session_state.quiz_selected == correct:
                    st.session_state.quiz_score += 1
                st.rerun()
        elif option_images:
            for k, v in options.items():
                st.markdown(f"#### {k}")
                render_option_body(k, v)
                st.divider()
            choice = st.radio(
                "Wähle deine Antwort:",
                option_keys,
                index=None,
                key=f"radio_{idx}",
                horizontal=True,
            )
            if st.button("Antwort bestätigen", disabled=(choice is None), type="primary"):
                st.session_state.quiz_selected = choice
                st.session_state.quiz_answered = True
                if choice == correct:
                    st.session_state.quiz_score += 1
                st.rerun()
        else:
            option_labels = [f"**{k}.** {v}" for k, v in options.items()]
            choice = st.radio(
                "Wähle deine Antwort:",
                option_labels,
                index=None,
                key=f"radio_{idx}",
            )
            if st.button("Antwort bestätigen", disabled=(choice is None), type="primary"):
                st.session_state.quiz_selected = option_keys[option_labels.index(choice)]
                st.session_state.quiz_answered = True
                if st.session_state.quiz_selected == correct:
                    st.session_state.quiz_score += 1
                st.rerun()
    else:
        selected = st.session_state.quiz_selected
        correct_set = set(correct)
        selected_set = set(selected)

        if option_images:
            for k, v in options.items():
                if k in correct_set:
                    st.success(f"#### ✅ {k}")
                elif k in selected_set and k not in correct_set:
                    st.error(f"#### ❌ {k}")
                else:
                    st.markdown(f"#### {k}")
                render_option_body(k, v)
                st.divider()
        else:
            for k, v in options.items():
                label = f"**{k}.** {v}"
                if k in correct_set:
                    st.success(f"✅ {label}")
                elif k in selected_set and k not in correct_set:
                    st.error(f"❌ {label}")
                else:
                    st.write(label)

        if selected == correct:
            st.success("**Richtig!**")
        else:
            st.error(f"**Falsch.** Die richtige Antwort ist **{correct}**.")

        if q.get("explanation"):
            with st.expander("Erklärung"):
                render_markdown(q["explanation"])

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
