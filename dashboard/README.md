# MovieLens Streamlit Dashboard

A Streamlit analytics dashboard querying the existing Snowflake warehouse directly.

## Warehouse objects used

- `MOVIELENS.DEV.FCT_RATINGS`
- `MOVIELENS.DEV.FCT_GENOME_SCORES`
- `MOVIELENS.DEV.DIM_MOVIES`
- `MOVIELENS.DEV.DIM_USERS`
- `MOVIELENS.DEV.DIM_GENOME_TAGS`

The dashboard does not create or modify Snowflake tables.

## 1. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 2. Configure Snowflake credentials

Copy the example secrets file:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Edit `.streamlit/secrets.toml` and enter your Snowflake account identifier, username, and password. Keep this file private; it is excluded by `.gitignore`.

The database, schema, warehouse, and role are prefilled from the verified session:
`MOVIELENS`, `DEV`, `COMPUTE_WH`, `ACCOUNTADMIN`.

## 3. Run

```bash
streamlit run app.py
```

## Notes

- Streamlit caches query results for 10 minutes.
- Use the Refresh cached data button on the home page after warehouse changes.
- Genre analysis uses `LATERAL FLATTEN` on `DIM_MOVIES.GENRE_ARRAY`.
- The minimum-rating filter in Movie Performance reduces the chance of ranking a movie based on very few ratings.
- This is an initial analytics implementation. Validate results and business definitions before treating them as final reporting metrics.
