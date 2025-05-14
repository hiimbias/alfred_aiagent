from modules.openai import OpenAIExecutor
from app.clients.clients import OPENAI_CLIENT
from app.core.resources.prompt import ALFRED
from app.core.config import settings
from modules.tools.get_weather import get_weather_tool

def get_jarvis_agent():
    return OpenAIExecutor(
    client = OPENAI_CLIENT,
    tools = [get_weather_tool],
    temperature = 0.3,
    model = settings.OPENAI_MODEL,
    system_message = ALFRED,
)
    
JARVIS_AGENT = get_jarvis_agent()