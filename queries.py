import sqlite3
import pandas as pd

def get_connection():
    return sqlite3.connect("citypulse.db")

def complaints_by_borough():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT borough, COUNT(*) as total_complaints
        FROM complaints
        WHERE borough != 'Unspecified'
        GROUP BY borough
        ORDER BY total_complaints DESC
    """, conn)
    conn.close()
    return df

def top_complaint_types(limit=10):
    conn = get_connection()
    df = pd.read_sql(f"""
        SELECT complaint_type, COUNT(*) as total
        FROM complaints
        GROUP BY complaint_type
        ORDER BY total DESC
        LIMIT {limit}
    """, conn)
    conn.close()
    return df

def complaints_by_status():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT status, COUNT(*) as total
        FROM complaints
        WHERE status != 'Unspecified'
        GROUP BY status
        ORDER BY total DESC
    """, conn)
    conn.close()
    return df

def top_agencies(limit=10):
    conn = get_connection()
    df = pd.read_sql(f"""
        SELECT agency_name, COUNT(*) as total
        FROM complaints
        GROUP BY agency_name
        ORDER BY total DESC
        LIMIT {limit}
    """, conn)
    conn.close()
    return df

def complaint_type_by_borough():
    conn = get_connection()
    df = pd.read_sql("""
        SELECT borough, complaint_type, COUNT(*) as total
        FROM complaints
        WHERE borough != 'Unspecified'
        GROUP BY borough, complaint_type
        ORDER BY borough, total DESC
    """, conn)
    conn.close()
    return df

def run_custom_query(sql):
    conn = get_connection()
    try:
        df = pd.read_sql(sql, conn)
        conn.close()
        return df, None
    except Exception as e:
        conn.close()
        return None, str(e)