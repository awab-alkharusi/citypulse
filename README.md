# CityPulse NYC 311 Analytics Dashboard

An AI-powered analytics dashboard built on 100,000+ real NYC 311 service requests. Ask questions in plain English and get instant SQL-powered answers with interactive charts.

## Live Demo
View the app here: YOUR_STREAMLIT_URL_HERE

## What It Does
- Visualizes complaint patterns across NYC boroughs, agencies, and complaint types
- Lets users query the dataset in plain English
- Automatically generates and executes SQL queries using Llama 3 via Groq API
- Returns results as interactive charts and data tables

## Tech Stack
- Python
- SQLite
- Pandas
- Plotly
- Streamlit
- Groq API and Llama 3 for text-to-SQL

## How It Works
1. User types a plain English question
2. Question sent to Llama 3 via Groq API with database schema as context
3. Model returns a valid SQL query
4. Query runs against SQLite database of 100K NYC complaints
5. Results return as a Pandas DataFrame
6. Plotly renders a chart automatically
7. Streamlit displays everything in the browser

## Data Source
NYC Open Data, 311 Service Requests 2024, 100,000 records