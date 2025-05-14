from app.clients.clients import OPENAI_CLIENT
from app.core.resources.prompt import ALFRED
from app.core.config import settings
from app.core.agent import JARVIS_AGENT
from app.core.services.auth import authenticate
from app.core.exceptions import AuthenticationError