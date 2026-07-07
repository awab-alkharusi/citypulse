import sqlite3
import pandas as pd

conn = sqlite3.connect("citypulse.db")

# How many complaints per borough?
print("=== COMPLAINTS BY BOROUGH ===")
df = pd.read_sql("SELECT borough, COUNT(*) as total FROM complaints GROUP BY borough ORDER BY total DESC", conn)
print(df.to_string())

# Top 10 complaint types
print("\n=== TOP 10 COMPLAINT TYPES ===")
df = pd.read_sql("SELECT complaint_type, COUNT(*) as total FROM complaints GROUP BY complaint_type ORDER BY total DESC LIMIT 10", conn)
print(df.to_string())

# Top 10 agencies
print("\n=== TOP 10 AGENCIES ===")
df = pd.read_sql("SELECT agency_name, COUNT(*) as total FROM complaints GROUP BY agency_name ORDER BY total DESC LIMIT 10", conn)
print(df.to_string())

# Status breakdown
print("\n=== STATUS BREAKDOWN ===")
df = pd.read_sql("SELECT status, COUNT(*) as total FROM complaints GROUP BY status ORDER BY total DESC", conn)
print(df.to_string())

conn.close()