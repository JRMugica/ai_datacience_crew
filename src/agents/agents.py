import crewai
import crewai_tools
import os
import torch
import src.utils as utils
from src.agents.agents_data_science import create_data_science_agents

config = utils.get_config()

def create_agents_crewai(model_choice):
    """
    CrewAI.
    """

    # Connecting to an OpenAI-compatible LLM
    if model_choice == 'External OpenAI API (data sensitive)':
        llm = crewai.LLM(
            model="gpt-4o-mini", #"gpt-4o",
            api_key=os.environ['OPENAI_API_KEY'],
            api_base=os.environ['OPENAI_API_BASE']
        )
    else:
        torch.cuda.empty_cache()
        llm = crewai.LLM(
            model=f"ollama/{model_choice}",
            base_url="http://localhost:11434", streaming=True
        )

    # Create Data Science agents if needed
    data_analyst_agents, data_analyst_tasks = create_data_science_agents(llm)

    manager_agent = crewai.Agent(
        role='Manager',
        goal=f'Delegate the steps to other agents.',
        backstory="""PMP certified project manager""",
        llm=llm
    )
    main_task = crewai.Task(
        description="""Give a proper answer to user message 
            and coordinate execution across agents: {user_message}.
            Use the provided conversation history: {context}.
            
            1. If no data is involved: use Personal Assistant agent
            2. If data is involved use Data Analyst agent and Data Scientist agents
            """,
        expected_output="proper answer to request",
        agent=manager_agent
    )
    assistant_agent  = crewai.Agent(
        role="Personal Assistant",
        goal="Support user",
        backstory=f""" You are experienced personal assistant    
        """,
        llm=llm,
        allow_delegation=False
    )
    assistant_task = crewai.Task(
        description=""" Support the manager to answer user query 
        """,
        expected_output="Answer to user",
        agent=assistant_agent,
    )

    crew = crewai.Crew(
        agents=[] + data_analyst_agents,
        manager_agent=manager_agent,
        tasks=[main_task, assistant_task]+data_analyst_tasks,
        memory=True,
        verbose=True,
        #process=crewai.Process.hierarchical,
        process=crewai.Process.sequential,
        planning=True
    )

    return crew

