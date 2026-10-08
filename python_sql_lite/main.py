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

SINGLE_DOMAIN_EXAMPLES = """Here are some example questions and correct SQL for this database:

Question: Who are the groomsmen?
SQL: SELECT g.first, g.last FROM guests g JOIN wedding_party wp ON wp.guest_id = g.id WHERE wp.role = 'groomsman';

Question: How many guests attended the Reception?
SQL: SELECT COUNT(*) FROM rsvps r JOIN events e ON e.id = r.event_id WHERE e.event_name = 'Reception' AND r.attended = 1;
"""

CROSS_DOMAIN_EXAMPLES = """Here is an example from a different database:

CREATE TABLE customers (customer_id INT PRIMARY KEY, firstname TEXT, lastname TEXT, city TEXT);
CREATE TABLE menu (menu_id INT PRIMARY KEY, menu_name TEXT, unit_price REAL);
CREATE TABLE orders (orderid INT, menu_id INT, quantity INT, customer_id INT,
    FOREIGN KEY (menu_id) REFERENCES menu(menu_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id));

Question: Which customers from Bangkok ordered a Latte?
SQL: SELECT DISTINCT c.firstname, c.lastname FROM customers c JOIN orders o ON o.customer_id = c.customer_id JOIN menu m ON m.menu_id = o.menu_id WHERE c.city = 'Bangkok' AND m.menu_name = 'Latte';
"""

# def get_sql_zero_shot(client, question):
#     prompt = f"""You are an expert at writing SQLite queries.
# Here is the database schema for a wedding:
# {SCHEMA}

# Write one SQLite query that answers the question below.
# Respond with ONLY the SQL query, no explanation.

# Question: {question}"""

#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[{"role": "user", "content": prompt}],
#     )
#     return response.choices[0].message.content

# def get_sql_single_domain(client, question, conn):
#     prompt = f"""You are an expert at writing SQLite queries.
# Here is the database schema for a wedding:
# {SCHEMA}

# SINGLE_DOMAIN_EXAMPLES
# # {get_data_hints(conn)}

# Write one SQLite query that answers the question below.
# Respond with ONLY the SQL query, no explanation.

# Question: {question}"""

#     response = client.chat.completions.create(
#         model=MODEL,
#         messages=[{"role": "user", "content": prompt}],
#     )
#     return response.choices[0].message.content



def get_sql(client, conn, question, strategy):
    examples = ""
    if strategy == "single_domain":
        examples = SINGLE_DOMAIN_EXAMPLES
    elif strategy == "cross_domain":
        examples = CROSS_DOMAIN_EXAMPLES

    prompt = f"""You are an expert at writing SQLite queries.
Here is the database schema for a wedding:
{SCHEMA}

More Context:
{examples}

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

def main(conn, question, strategy):
    with open("auth.json", "r") as f:
        auth = json.load(f)
    client = OpenAI(api_key=auth["api_key"])

    sql = clean_sql(get_sql(client, conn, question, strategy) )
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
    print()



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--strategy", default="zero_shot", choices=["zero_shot", "single_domain", "cross_domain"])
    parser.add_argument("--query", type=str, default="Who are the bride's sisters?")
    args = parser.parse_args()
    conn = create_connection(DATABASE)

    main(conn, question=args.query, strategy=args.strategy)
