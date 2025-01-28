import crewai
import crewai_tools
import os
import src.utils as utils
from src.agents.agents_data_science import create_data_science_agents

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

    # Create Data Science agents if needed
    data_analyst_agents, data_analyst_tasks = create_data_science_agents(llm)

    agents = [] + data_analyst_agents
    tasks = [] + data_analyst_tasks

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
        agents=agents,
        manager_agent=manager_agent,
        tasks=[main_task]+tasks,
        #process=crewai.Process.sequential,
        verbose=True
    )

    return crew

