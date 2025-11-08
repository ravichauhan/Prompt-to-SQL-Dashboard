from textwrap import dedent


BASE_PROMPT = "Convert this English query into valid SQL for the following schema..."


def build_prompt(natural_language: str, schema_ddl: str) -> str:
    template = f"""\
    {BASE_PROMPT}

    Schema:
    {schema_ddl}

    Instructions:
    - Only return the SQL query, no commentary.
    - Use valid SQLite syntax.
    - Prefer existing columns and avoid SELECT *.
    - If aggregation is requested, alias the column using snake_case.

    English query:
    {natural_language}
    """
    return dedent(template)
