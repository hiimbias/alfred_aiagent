# J.A.R.V.I.S

This is my personal project to represent a personal AIAgent built. It enables natural conversation between users and an intelligent assistant, making it suitable for tasks like personal productivity, customer support, or learning companions. 
Note: This project is still under development. Some features may not be fully available yet.

---

## Project Structure
```bash
.
├── app ## UI directory
│   ├── clients
│   │   ├── clients.py
│   │   └── __init__.py
│   ├── components
│   │   ├── agent.py
│   │   ├── config.py
│   │   ├── exceptions
│   │   │   ├── authentication_error.py
│   │   │   └── __init__.py
│   │   ├── __init__.py
│   │   ├── resources
│   │   │   ├── __init__.py
│   │   │   └── prompt.py
│   │   └── services
│   │       ├── auth.py
│   │       └── __init__.py
│   ├── __init__.py
│   └── main.py
├── core ## base directory
│   ├── handlers
│   │   ├── __init__.py
│   │   └── tool_handler.py
│   ├── __init__.py
│   ├── interfaces
│   │   ├── base_embedding_model.py
│   │   ├── base_executor.py
│   │   ├── base_llm_model.py
│   │   ├── base_speech_model.py
│   │   ├── base_tool_handler.py
│   │   └── __init__.py
│   ├── models
│   │   ├── __init__.py
│   │   ├── io
│   │   │   ├── embedding_unit.py
│   │   │   └── __init__.py
│   │   ├── responses
│   │   │   ├── embedding_response.py
│   │   │   ├── __init__.py
│   │   │   ├── openagent_response.py
│   │   │   └── usage_response.py
│   │   └── tool_responses
│   │       ├── __init__.py
│   │       ├── tool_response.py
│   │       └── weather_response.py
│   ├── _types
│   │   ├── __init__.py
│   │   └── named_byte_io.py
│   └── utils
│       ├── audio_utils.py
│       ├── __init__.py
│       └── tool_wrapper.py
├── modules ## logic modules directory
│   ├── database
│   │   └── __init__.py
│   ├── __init__.py
│   ├── openai
│   │   ├── __init__.py
│   │   ├── openai_embedding_service.py
│   │   ├── openai_executor.py
│   │   ├── openai_llm_service.py
│   │   └── openai_speech_model.py
│   └── tools
│       ├── get_weather.py
│       ├── __init__.py
│       └── retrieve_knowledge.py
├── requirements.txt
└── test
    ├── basic_agent_use copy.ipynb
    └── basic_agent_use.ipynb

21 directories, 50 files
```

---

## Architecture
- `core/interfaces`: Abstract base classes for LLM, embedding, and tool components  
- `core/models`: Pydantic models for structured, type-safe data  
- `core/handlers`: Classes to handle tools and logic execution  
- `core/utils`: Utilities and wrappers  
- `modules`: Implementations for services and tool integrations (e.g., OpenAI, weather)  
- `app`: Streamlit UI and authentication layer  

## Features

- Clean and interactive chat interface with Streamlit
- User authentication (username & password)
- Saves and restores chat history
- Tools intergration
- Type-safe codebase using Pydantic models  
- Working well with OPENAI API - Still workings on extensions for other LLM providers

---

## Installation and Running
### 1. Clone the repository

```bash
git clone https://github.com/hiimbias/alfred_aiagent.git
cd aiagent
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Fill your own API key in file .env

### 4. Run app
```bash
PYTHONPATH=. streamlit run app/main.py
```


