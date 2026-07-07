from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SCHEMA = """
You are a SQL expert. The database has one table called 'complaints' with these columns:
- unique_key: unique ID for each complaint
- created_date: when the complaint was filed (text, format: 2024-01-15T00:00:00.000)
- closed_date: when it was resolved (text, may be null)
- agency: short agency code (e.g. NYPD, DEP)
- agency_name: full agency name
- complaint_type: type of complaint (e.g. 'Illegal Parking', 'Noise - Residential')
- descriptor: more detail about the complaint
- status: current status (Closed, Open, In Progress, Started, Assigned, Pending)
- borough: NYC borough (BROOKLYN, BRONX, QUEENS, MANHATTAN, STATEN ISLAND)
- city: city name

Rules:
- Always return ONLY a valid SQLite SQL query, nothing else
- No markdown, no explanation, no backticks
- Use LIMIT 500 maximum on any query
- borough values are uppercase
- For date filtering use: created_date LIKE '2024%'
"""

def generate_sql(user_question):
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SCHEMA},
            {"role": "user", "content": f"Write a SQL query to answer: {user_question}"}
        ],
        temperature=0
    )
    sql = response.choices[0].message.content.strip()
    # Clean up in case LLM adds backticks anyway
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql