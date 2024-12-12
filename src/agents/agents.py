import crewai
import crewai_tools
import os
import glob
import src.utils as utils
import src.tools as tools
from crewai.tasks.conditional_task import ConditionalTask

config = utils.read_config()
UPLOAD_FOLDER = os.path.join(os.getcwd(), config['parameters']['UPLOAD_FOLDER'])
utils.set_api_keys()

def create_agents_crewai():
    """
    CrewAI.
    """

    # Connecting to an OpenAI-compatible LLM
    llm = crewai.LLM(
        model="gpt-4o-mini", #"gpt-4o",
        api_key=os.environ['OPENAI_API_KEY'],
        api_base=os.environ['OPENAI_API_BASE']
    )

    assistant_agent = crewai.Agent(
        role="Assistant Agent",
        goal="""Support user requests
            """,
        backstory="""You are a personal assistant""",
        tools=[],
        llm=llm,
        allow_code_execution=False,
        allow_delegation=False
    )
    assistant_task = crewai.Task(
        description="""Understand and answer user message""",
        agent=assistant_agent,
        expected_output="Anwser to user"
    )

    data_analyst_agents = []
    data_analyst_tasks = []
    if len(os.listdir(UPLOAD_FOLDER)) > 0:

        query_agent  = crewai.Agent(
            role="Senior Database Developer",
            goal="Construct and execute SQL queries based on a request",
            backstory="""
                You are an experienced database engineer who is master at creating efficient and complex SQL queries.
                You have a deep understanding of how different databases work and how to optimize queries.
                Use the `list_tables` to find available tables.
                Use the `tables_schema` to understand the metadata for the tables.
                Use the `check_sql` to check your queries for correctness.
                Use the `execute_sql` to execute queries against the database.
            """,
            llm=llm,
            tools= tools.data_query_tools(),
            allow_delegation=False,
        )
        extract_data_task = crewai.Task(
            description="Extract data that is required for the query {message}.",
            expected_output="Database result for the query",
            agent=query_agent,
        )

        data_analyst_agent = crewai.Agent(
            role="Senior Data Analyst",
            goal="You receive data from the database developer and analyze it",
            backstory="""
                You have deep experience with analyzing datasets using Python.
                Your work is always based on the provided data and is clear,
                easy-to-understand and to the point. You have attention
                to detail and always produce very detailed work (as long as you need).
            """,
            llm=llm,
            allow_delegation=False
        )
        analyze_data_task = crewai.Task(
            description="Analyze the data from the database and write an analysis for {message}.",
            expected_output="Detailed analysis text",
            agent=data_analyst_agent,
            context=[extract_data_task],
        )

        data_viz_agent = crewai.Agent(
            role="Senior Business Inteligence Analyst",
            goal="""You receive data from the analysis from Data Scientist,
                 create a Plotly code and store it using FileWriterTool 
                 if user requests it on his query: {message}
                 """,
            backstory="""
                You have deep experience on data visualization using Python and Plotly.
                Your work is always based on the provided data and is clear,
                easy-to-understand and to the point. If user requests it, you create
                nice plots using Plotly, otherwise you just deliver the same data you received.
            """,
            llm=llm,
            allow_delegation=False,
            allow_code_execution=True
        )
        plot_data_task = crewai.Task(
            description="""Check if plot is requested.
                        If so, deliver proper plotly chart python code.
                        Store plot at fig variable.
                        Do not run fig.show()
                        """,
            expected_output="Plotly chart",
            agent=data_viz_agent,
            context=[analyze_data_task],
        )

        data_analyst_agents = [query_agent, data_analyst_agent, data_viz_agent]
        data_analyst_tasks = [extract_data_task, analyze_data_task, plot_data_task]

    manager_agent = crewai.Agent(
        role='Manager',
        goal=f'Delegate the steps to other agents.',
        backstory="""PMP certified project manager""",
        llm=llm
    )
    main_task = crewai.Task(
        description="""Give a proper answer to user message 
            and coordinate execution across agents: {message}
            """,
        expected_output="proper answer to request",
        agent=manager_agent
    )
    crew = crewai.Crew(
        agents=[assistant_agent]+data_analyst_agents,
        manager_agent=manager_agent,
        tasks=[main_task, assistant_task]+data_analyst_tasks,
        process=crewai.Process.sequential,
        verbose=True
    )

    return crew

