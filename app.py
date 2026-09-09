import streamlit as st
import plotly.express as px
import os
import requests
import pandas as pd
import sqlite3
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(
    page_title="CityPulse NYC",
    page_icon="icon_city.jpg",
    layout="wide"
)

def build_database():
    url = (
        "https://data.cityofnewyork.us/resource/erm2-nwe9.csv"
        "?$limit=100000"
        "&$where=created_date>'2024-01-01'"
        "&$order=created_date DESC"
    )
    response = requests.get(url, timeout=120)
    os.makedirs("data", exist_ok=True)
    with open("data/nyc311_sample.csv", "w", encoding="utf-8") as f:
        f.write(response.text)
    df = pd.read_csv("data/nyc311_sample.csv")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    columns_to_keep = [
        "unique_key", "created_date", "closed_date", "agency",
        "agency_name", "complaint_type", "descriptor",
        "status", "borough", "city"
    ]
    columns_to_keep = [col for col in columns_to_keep if col in df.columns]
    df = df[columns_to_keep]
    df = df.dropna(subset=["borough"])
    conn = sqlite3.connect("citypulse.db")
    df.to_sql("complaints", conn, if_exists="replace", index=False)
    conn.close()

def get_connection():
    return sqlite3.connect("citypulse.db")

def generate_sql(user_question):
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    #client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    schema = """
You are a SQL expert. The database has one table called 'complaints' with these columns:
unique_key, created_date, closed_date, agency, agency_name, complaint_type,
descriptor, status, borough, city.
Borough values are uppercase: BROOKLYN, BRONX, QUEENS, MANHATTAN, STATEN ISLAND.
Status values: Closed, Open, In Progress, Started, Assigned, Pending.
Return ONLY valid SQLite SQL. No markdown, no backticks, no explanation. Use LIMIT 500 max.
"""
    response = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": schema},
            {"role": "user", "content": f"Write SQL to answer: {user_question}"}
        ],
        temperature=0
    )
    sql = response.choices[0].message.content.strip()
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql

# Check if database exists, build it if not
if not os.path.exists("citypulse.db"):
    st.title("CityPulse — NYC 311 Analytics Dashboard")
    with st.spinner("Setting up database for first time... this takes about 30 seconds."):
        build_database()
    st.success("Database ready!")
    st.rerun()

# Database exists, show the app
st.title("CityPulse — NYC 311 Analytics Dashboard")
st.markdown("Explore 100,000+ NYC service requests. Ask questions in plain English or explore the charts below.")
st.divider()

conn = get_connection()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Complaints by Borough")
    df = pd.read_sql("""
        SELECT borough, COUNT(*) as total_complaints
        FROM complaints
        WHERE borough != 'Unspecified'
        GROUP BY borough ORDER BY total_complaints DESC
    """, conn)
    fig = px.bar(df, x="borough", y="total_complaints", color="borough",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Complaints by Status")
    df = pd.read_sql("""
        SELECT status, COUNT(*) as total FROM complaints
        WHERE status != 'Unspecified'
        GROUP BY status ORDER BY total DESC
    """, conn)
    fig = px.pie(df, names="status", values="total",
                 color_discrete_sequence=px.colors.qualitative.Set2)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.subheader("Top 10 Complaint Types")
    df = pd.read_sql("""
        SELECT complaint_type, COUNT(*) as total FROM complaints
        GROUP BY complaint_type ORDER BY total DESC LIMIT 10
    """, conn)
    fig = px.bar(df, x="total", y="complaint_type", orientation="h",
                 color="total", color_continuous_scale="Blues")
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Top 10 Agencies by Volume")
    df = pd.read_sql("""
        SELECT agency_name, COUNT(*) as total FROM complaints
        WHERE agency_name IS NOT NULL AND agency_name != ''
        GROUP BY agency_name ORDER BY total DESC LIMIT 10
    """, conn)
    fig = px.bar(df, x="total", y="agency_name", orientation="h",
                 color="total", color_continuous_scale="Greens")
    fig.update_layout(
        yaxis={"categoryorder": "total ascending"},
        xaxis_range=[0, df["total"].max() * 1.1]
    )
    st.plotly_chart(fig, use_container_width=True)

conn.close()

st.divider()

st.subheader("Ask the Data a Question")
st.markdown("Type a question in plain English and the AI will generate SQL and return the results.")

user_question = st.text_input(
    "Your question:",
    placeholder="e.g. Which borough has the most open complaints?"
)

if user_question:
    with st.spinner("Generating SQL and querying database..."):
        sql = generate_sql(user_question)
        st.code(sql, language="sql")
        try:
            conn2 = get_connection()
            result_df = pd.read_sql(sql, conn2)
            conn2.close()
            st.dataframe(result_df, use_container_width=True)
            if len(result_df.columns) == 2:
                col_names = result_df.columns.tolist()
                try:
                    fig = px.bar(result_df, x=col_names[0], y=col_names[1],
                                 color_discrete_sequence=["#636EFA"])
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    pass
        except Exception as e:
            st.error(f"Query failed: {e}")

st.divider()
st.caption("Data source: NYC Open Data 311 Service Requests | Powered by Groq Llama 3")
