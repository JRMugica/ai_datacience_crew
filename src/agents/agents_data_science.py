import crewai_tools
import crewai
import src.tools as tools
import src.utils as utils
from langchain_community.utilities.sql_database import SQLDatabase


config = utils.get_config()
data_folder = config['parameters']['UPLOAD_FOLDER']

def create_data_science_agents(llm):

    db = utils.database_creation(data_folder)
    if isinstance(db, SQLDatabase):
        db_tools = tools.data_query_tools(db)
    else:
        return [], []

    query_agent  = crewai.Agent(
        role="Data Analyst",
        goal="Construct and execute SQL queries based on a request",
        backstory=f"""
            You are an experienced database engineer who is master at creating efficient and complex SQL queries.
            You have a deep understanding of how different databases work and how to optimize queries.
            1. Use `list_tables` to find available tables.
            2. Use `tables_schema` to understand the metadata for the tables.
            3. Use `check_sql` to check your queries for correctness.
            4. Use `execute_sql` to execute queries against the database.
            5. Format the obtained data as csv and use 'FileWriterTool' to store the results at file '{data_folder}/results.csv'              
        """,
        llm=llm,
        tools= db_tools +[crewai_tools.FileWriterTool()],
        allow_delegation=False
    )
    extract_data_task = crewai.Task(
        description="Extract data that is required for the query {user_message}.",
        expected_output="Database result for the query in csv format",
        agent=query_agent,
    )

    python_agent  = crewai.Agent(
        role="Data Scientist",
        goal="Understand if python is needed to perform the request and use it if needed",
        backstory=f"""
            You are an experienced Data Scientist who is master at using python to do forecasting and data processing.
            1. Create python code script that: 
                1.1 Reads in pandas the data
                1.2 Creates the python code requested: it can be machine learning for forecasting, or for data preparation, or any other
                    When forcasting is on time series data, use arima forecast approach finding best parameters using last periods out of time validation
                    When forcasting in on tabular data, use Random Forest approach with 5-fold hyperparameter tuning
                1.3 Delivers expected data output
            2. Execute the python code.
            3. Format the obtained data as csv and use 'FileWriterTool' to store the results at file '{data_folder}/results_python.csv'    
            4. As backup write the python script used using 'FileWriterTool' to store the script at file '{data_folder}/results_python_script.py'
            5. Show the final data to the user           
        """,
        llm=llm,
        tools= [crewai_tools.FileWriterTool()],
        allow_delegation=False,
        allow_code_execution=True,
        code_execution_mode = 'unsafe'
    )
    python_task = crewai.Task(
        description="Understand if python is needed to acomplish user request: {user_message}.",
        expected_output="Python script execution and final data result shared to the user",
        agent=python_agent,
        context=extract_data_task
    )

    data_analyst_agents = [query_agent, python_agent]
    data_analyst_tasks = [extract_data_task, python_task]

    return data_analyst_agents, data_analyst_tasks