import argparse
import json

from openai import OpenAI
# input stuff
from db import create_connection
from schema import (
    sql_create_guests_table,
    sql_create_wedding_party_table,
    sql_create_events_table,
    sql_create_gifts_table,
    sql_create_rsvps_table,
)

DATABASE = "./wedding.db"
MODEL = "gpt-6-luna"

SCHEMA = "\n".join([
    sql_create_guests_table,
    sql_create_wedding_party_table,
    sql_create_events_table,
    sql_create_gifts_table,
    sql_create_rsvps_table,
])


def get_sql(client, question):
    prompt = f"""You are an expert at writing SQLite queries.
Here is the database schema for a wedding:
{SCHEMA}

Write one SQLite query that answers the question below.
Respond with ONLY the SQL query, no explanation.

Question: {question}"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

# response stuff
def clean_sql(sql):
    sql = sql.strip()
    if sql.startswith("```"):
        sql = sql.split("\n", 1)[1]
        sql = sql.rsplit("```", 1)[0] 
    return sql.strip()

def run_sql(conn, sql):
    if not sql.lower().startswith(("select", "with")):
        raise ValueError("Only SELECT queries are allowed")
    cur = conn.cursor()
    cur.execute(sql)
    columns = [col[0] for col in cur.description]
    rows = cur.fetchall()
    return columns, rows

def get_answer(client, question, sql, columns, rows):
    prompt = f"""A user asked a question about a wedding database.

Question: {question}
SQL query used: {sql}
Columns: {columns}
Results: {rows}

Answer the question in friendly, plain English using only these results.
If the results are empty, say that nothing matched."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content

def main(conn, question):
    with open("auth.json", "r") as f:
        auth = json.load(f)
    client = OpenAI(api_key=auth["api_key"])

    sql = get_sql(client, question)
    sql = clean_sql(get_sql(client, question))
    print("Question:", question)
    print("SQL:", sql)

    try:
        columns, rows = run_sql(conn, sql)
    except Exception as e:
        print("Query failed:", e)
        return

    print("Rows:", rows)
    answer = get_answer(client, question, sql, columns, rows)
    print("Answer:", answer)



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--query", type=str, default="Who are the bride's sisters?")
    args = parser.parse_args()
    conn = create_connection(DATABASE)

    main(conn, question=args.query)
