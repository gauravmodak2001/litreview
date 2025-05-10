# Automated Literature Review System

A modular Python system for automated literature reviews that searches, retrieves, filters, and summarizes academic papers.

## Features

- 🔍 **Search**: Find relevant academic papers across multiple sources
- 📄 **Retrieval**: Extract full text and additional metadata from papers
- 🔎 **Filtering**: Assess and filter papers based on relevance to the topic
- 📝 **Summarization**: Generate comprehensive literature reviews from papers

## Overview

This system provides both:
- **Web Interface**: A Flask-based web application for easy use through a browser
- **Command Line Interface**: Direct CLI access for scripting and automation

The application can run in two modes:
- **Full Mode**: Using Ollama for local LLM-powered processing
- **Demo Mode**: Fallback mode with pre-defined examples when Ollama is not available

## Installation

1. Clone this repository
2. Install the required dependencies (see `dependencies_list.md`)
3. For full functionality, install [Ollama](https://ollama.com/download)
4. Download a language model (e.g., `ollama pull llama2`)

## Usage

### Web Interface

Run the web application:

```bash
python main.py
```

Or with Gunicorn (recommended for production):

```bash
gunicorn --bind 0.0.0.0:5000 app:app
```

Then open your browser to http://localhost:5000

### Command Line

Run a literature review from the command line:

```bash
python main.py "your research topic here"
```

## Project Structure

- `app.py`: Flask web application
- `main.py`: Entry point with web/CLI support
- `literature_review/`: Core package
  - `models.py`: Data models
  - `search_agent.py`: Paper search functionality
  - `content_agent.py`: Full-text retrieval
  - `filter_agent.py`: Relevance assessment
  - `summary_agent.py`: Literature review generation
  - `review_orchestrator.py`: Process coordination
  - `utils.py`: Helper functions
  - `mock_data.py` & `mock_orchestrator.py`: Demo mode support
- `templates/`: HTML templates for the web interface

## Configuration

Environment variables:
- `LLM_MODEL`: Ollama model name (default: "llama2")
- `SESSION_SECRET`: Secret key for Flask sessions

## Requirements

- Python 3.9+
- Dependencies listed in `dependencies_list.md`
- Optional: Ollama for full functionality
   