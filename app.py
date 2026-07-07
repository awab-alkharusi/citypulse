import streamlit as st
import plotly.express as px
import os
from queries import (
    complaints_by_borough,
    top_complaint_types,
    complaints_by_status,
    top_agencies,
    run_custom_query
)
from llm import generate_sql

def setup_database():
    if not os.path.exists("citypulse.db"):
        import requests
        import pandas as pd
        import sqlite3
        
        print("Downloading data...")
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
        print("Database ready.")

setup_database()

# Page config
st.set_page_config(
    page_title="CityPulse NYC",
    page_icon="icon_philly.jpg", # site icon as the historic Philadelphia
    layout="wide"
)

# Header using Streamlit framework
st.title("CityPulse — NYC 311 Analytics Dashboard")
st.markdown("Explore 100,000+ NYC service requests. Ask questions in plain English or explore the pre-built charts below.")
st.divider()

# Row 1: Borough + Status
col1, col2 = st.columns(2)

with col1:
    st.subheader("Complaints by Borough")
    df = complaints_by_borough()
    fig = px.bar(
        df,
        x="borough",
        y="total_complaints",
        color="borough",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Complaints by Status")
    df = complaints_by_status()
    fig = px.pie(
        df,
        names="status",
        values="total",
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Row 2: Complaint types + Agencies
col3, col4 = st.columns(2)

with col3:
    st.subheader("Top 10 Complaint Types")
    df = top_complaint_types(10)
    fig = px.bar(
        df,
        x="total",
        y="complaint_type",
        orientation="h",
        color="total",
        color_continuous_scale="Blues"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Top 10 Agencies by Volume")
    df = top_agencies(10)
    fig = px.bar(
        df,
        x="total",
        y="agency_name",
        orientation="h",
        color="total",
        color_continuous_scale="Greens"
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Natural Language Query Section
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

        df, error = run_custom_query(sql)

        if error:
            st.error(f"Query failed: {error}")
        elif df is not None and len(df) > 0:
            st.dataframe(df, use_container_width=True)

            # Auto chart if results have exactly 2 columns
            if len(df.columns) == 2:
                col_names = df.columns.tolist()
                try:
                    fig = px.bar(
                        df,
                        x=col_names[0],
                        y=col_names[1],
                        color_discrete_sequence=["#636EFA"]
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except:
                    pass
        else:
            st.warning("Query returned no results.")

st.divider()
st.caption("Data source: NYC Open Data 311 Service Requests | Powered by Groq Llama 3 API")