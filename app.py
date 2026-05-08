import streamlit as st
from utils.questions import stats, TOPICS

st.set_page_config(
    page_title="Databricks Exam Trainer",
    page_icon="🏗️",
    layout="wide",
)

st.title("🏗️ Databricks Data Engineer Associate")
st.caption("Prüfungsvorbereitung — Exam-Version ab 4. Mai 2026")

st.info(
    "**Prüfungsformat:** 45 Multiple-Choice-Fragen  •  90 Minuten  •  Online oder Testcenter",
    icon="ℹ️",
)

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Themenübersicht")
    topic_descriptions = {
        "Databricks Intelligence Platform": "Architektur, Delta Lake, Unity Catalog, Compute-Typen",
        "Data Ingestion and Loading": "Auto Loader, COPY INTO, Lakeflow Connect, JDBC/ODBC",
        "Data Transformation and Modeling": "PySpark/SQL, Joins, Aggregationen, Gold-Layer-Objekte",
        "Working with Lakeflow Jobs": "Orchestrierung, DAG, Scheduling, Trigger-Typen",
        "Implementing CI/CD": "DABs, Databricks Repos, Databricks CLI",
        "Troubleshooting, Monitoring, and Optimization": "Spark UI, Liquid Clustering, Cluster-Diagnose",
        "Governance and Security": "Unity Catalog, GRANT/REVOKE, Row-/Column-Security, ABAC",
    }
    for topic, desc in topic_descriptions.items():
        with st.expander(f"**{topic}**"):
            st.write(desc)
            subtopics = TOPICS.get(topic, [])
            for sub in subtopics:
                st.markdown(f"- {sub}")

with col2:
    st.subheader("Fragenbank")
    s = stats()
    st.metric("Fragen gesamt", s["total"])
    if s["by_topic"]:
        st.write("**Nach Thema:**")
        for topic, count in sorted(s["by_topic"].items()):
            short = topic.split(" ")[0:3]
            st.write(f"- {' '.join(short)}…: **{count}**")

    st.divider()
    st.subheader("Navigation")
    st.page_link("pages/1_Quiz.py", label="📝 Quiz starten", icon="▶️")
    st.page_link("pages/2_Fragen_Hinzufuegen.py", label="➕ Frage manuell hinzufügen")
    st.page_link("pages/3_KI_Generator.py", label="🤖 KI-Fragen generieren")
