import crewai
import crewai_tools
import os
import glob
from src.utils.prepare_environment import set_api_keys, read_config

config = read_config()
UPLOAD_FOLDER = os.path.join(os.getcwd(), config['parameters']['UPLOAD_FOLDER'])

def create_agents_crewai():
    """
    CrewAI.
    """
    set_api_keys()

    # Connecting to an OpenAI-compatible LLM
    openai_llm = crewai.LLM(
        model="gpt-4o",
        api_key=os.environ['OPENAI_API_KEY'],
        api_base=os.environ['OPENAI_API_BASE']
    )

    # Set of tools
    Global = [crewai_tools.DallETool()]
    FileRead = [crewai_tools.FileReadTool(f) for f in glob.glob(UPLOAD_FOLDER+'/*.txt')]
    TXTSearch = [crewai_tools.TXTSearchTool(f) for f in glob.glob(UPLOAD_FOLDER + '/*.txt')]
    PDFSearch = [crewai_tools.PDFSearchTool(f) for f in glob.glob(UPLOAD_FOLDER + '/*.pdf')]
    CSVSearch = [crewai_tools.CSVSearchTool(csv=f) for f in glob.glob(UPLOAD_FOLDER + '/*.csv')]
    tools = Global+FileRead+TXTSearch+PDFSearch+CSVSearch

    agent = crewai.Agent(
        role='Personal Assistant',
        goal='Support user on his requests',
        backstory="Personal Assistant, help the user with requests related to daily activities and productivity.",
        tools=tools,
        memory=True,
        llm=openai_llm
    )

    return agent

def process_message(agent, mensaje):
    """
    Procesa el mensaje del usuario y determina qué agente de CrewAI debe ejecutar.
    """

    give_answer = crewai.Task(
        description=f"""
            Assist on following user's query:
            {mensaje}
        """,
        expected_output="""
            Detailed answer to user query, including images if requested
        """,
        agent=agent
    )
    return agent.execute_task(give_answer)
