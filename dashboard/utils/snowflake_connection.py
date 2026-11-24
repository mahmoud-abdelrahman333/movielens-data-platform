import streamlit as st
import pandas as pd
import snowflake.connector


@st.cache_resource
def get_connection():
    cfg = st.secrets["snowflake"]

    return snowflake.connector.connect(
        account=cfg["account"],
        user=cfg["user"],
        password=cfg["password"],
        warehouse=cfg["warehouse"],
        database=cfg["database"],
        schema=cfg["schema"],
        role=cfg["role"],
    )
@st.cache_data(ttl=600, show_spinner="Querying Snowflake...")
def run_query(sql: str) -> pd.DataFrame:
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(sql)
        columns = [col[0] for col in cur.description]
        return pd.DataFrame(cur.fetchall(), columns=columns)
    finally:
        cur.close()
