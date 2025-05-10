# Dependencies for Literature Review System

Here's a list of the Python packages required for this project:

```
flask==2.3.3
gunicorn==23.0.0
browser-use==0.1.45
langchain-ollama==0.3.0
langchain-core==0.3.49
Flask-SQLAlchemy==3.1.1
email-validator==2.1.0
psycopg2-binary==2.9.9
```

## Installation Instructions

To install these dependencies, you can use pip:

```bash
pip install -r requirements.txt
```

Or install them individually:

```bash
pip install flask gunicorn browser-use langchain-ollama langchain-core Flask-SQLAlchemy email-validator psycopg2-binary
```

## Additional Requirements

For the full functionality (non-demo mode), you'll need:

1. **Ollama**: A local language model server. Download from [https://ollama.com/download](https://ollama.com/download)
2. **Language Models**: After installing Ollama, download a model like llama2:
   ```bash
   ollama pull llama2
   ```

## Environment Variables

You can configure the application with these environment variables:

- `LLM_MODEL`: The language model to use with Ollama (default: "llama2")
- `SESSION_SECRET`: Secret key for Flask sessions (default: a development key is used)