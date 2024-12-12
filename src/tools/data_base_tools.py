import os
from pathlib import Path
import glob
import pandas as pd
from crewai_tools import tool
import crewai
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDataBaseTool,
)
#from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
import sqlite3
from src.utils.prepare_environment import read_config

config = read_config()
UPLOAD_FOLDER = os.path.join(os.getcwd(), config['parameters']['UPLOAD_FOLDER'])

def data_query_tools():

    uri = f'{UPLOAD_FOLDER}/data_base.db'
    db = sqlite3.connect(uri)
    for f in glob.glob(f'{UPLOAD_FOLDER}/*.csv'):
        data = pd.read_csv(f)
        data.to_sql(
            name=Path(f).stem,
            con=db,
            if_exists="replace",
            index=False
        )

    @tool("list_tables")
    def list_tables() -> str:
        """List the available tables in the database"""
        uri = f'{UPLOAD_FOLDER}/data_base.db'
        uri_ = f"sqlite:///{Path(uri).as_posix()}"
        db = SQLDatabase.from_uri(uri_)
        return ListSQLDatabaseTool(db=db).invoke("")

    @tool("tables_schema")
    def tables_schema(tables: str) -> str:
        """
        Input is a comma-separated list of tables, output is the schema and sample rows
        for those tables. Be sure that the tables actually exist by calling `list_tables` first!
        Example Input: table1, table2, table3
        """
        uri = f'{UPLOAD_FOLDER}/data_base.db'
        uri_ = f"sqlite:///{Path(uri).as_posix()}"
        db = SQLDatabase.from_uri(uri_)
        tool = InfoSQLDatabaseTool(db=db)
        return tool.invoke(tables)

    @tool("execute_sql")
    def execute_sql(sql_query: str) -> str:
        """Execute a SQL query against the database. Returns the result"""
        uri = f'{UPLOAD_FOLDER}/data_base.db'
        uri_ = f"sqlite:///{Path(uri).as_posix()}"
        db = SQLDatabase.from_uri(uri_)
        return QuerySQLDataBaseTool(db=db).invoke(sql_query)

    llm = crewai.LLM(
        model="gpt-4o-mini",  # "gpt-4o",
        api_key=os.environ['OPENAI_API_KEY'],
        api_base=os.environ['OPENAI_API_BASE']
    )
    llm = ChatOpenAI(model="gpt-4o-mini")
    @tool("check_sql")
    def check_sql(sql_query: str) -> str:
        """
        Use this tool to double check if your query is correct before executing it. Always use this
        tool before executing a query with `execute_sql`.
        """
        uri = f'{UPLOAD_FOLDER}/data_base.db'
        uri_ = f"sqlite:///{Path(uri).as_posix()}"
        db = SQLDatabase.from_uri(uri_)
        return QuerySQLCheckerTool(db=db, llm=llm).invoke({"query": sql_query})

    return [list_tables, tables_schema, execute_sql, check_sql]