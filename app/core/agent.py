from modules.openai import OpenAIExecutor
from app.clients.clients import OPENAI_CLIENT
from app.core.resources.prompt import ALFRED
from app.core.config import settings

def get_jarvis_agent():
    return OpenAIExecutor(
    client = OPENAI_CLIENT,
    temperature = 0.3,
    model = settings.OPENAI_MODEL,
    system_message = ALFRED,
)
    
JARVIS_AGENT = get_jarvis_agent()