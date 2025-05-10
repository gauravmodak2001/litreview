"""
Flask web application for Automated Literature Review System using local Ollama.
"""
import os
import asyncio
import json
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from langchain_ollama import ChatOllama
from literature_review import LiteratureReviewOrchestrator

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_secret_key")

# Configure app
app.config["OUTPUT_DIR"] = "literature_review"
os.makedirs(app.config["OUTPUT_DIR"], exist_ok=True)

# Initialize language model with local Ollama
model_name = os.environ.get("LLM_MODEL", "llama2")
ollama_url = os.environ.get("OLLAMA_URL", "http://localhost:11434")

# Create the LLM with explicit Ollama URL
llm = ChatOllama(
    model=model_name,
    base_url=ollama_url,
    temperature=0.7,
    timeout=300  # 5 minute timeout for longer operations
)

# Create orchestrator with the local Ollama LLM
orchestrator = LiteratureReviewOrchestrator(llm)
app.config["DEMO_MODE"] = False

print(f"✅ Using local Ollama at {ollama_url} with model: {model_name}")

# Helper function to run async code
def run_async(coroutine):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coroutine)
    finally:
        loop.close()

@app.route('/')
def index():
    """Render the home page."""
    return render_template('index.html')

@app.route('/health')
def health():
    """Check if Ollama is running and accessible."""
    try:
        # Simple test to check if Ollama is responding
        test_response = llm.invoke("Say 'OK' if you're working")
        return jsonify({
            "status": "healthy",
            "ollama_url": ollama_url,
            "model": model_name,
            "response": str(test_response)[:100]  # First 100 chars of response
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "ollama_url": ollama_url,
            "model": model_name
        }), 500

@app.route('/review', methods=['GET', 'POST'])
def review():
    """Handle literature review requests."""
    if request.method == 'POST':
        # Get form data
        topic = request.form.get('topic')
        if not topic:
            flash('Please enter a topic', 'error')
            return redirect(url_for('index'))
        
        max_papers = int(request.form.get('max_papers', 15))
        max_full_text_papers = int(request.form.get('max_full_text_papers', 10))
        relevance_threshold = float(request.form.get('relevance_threshold', 0.7))
        
        try:
            # Run literature review
            results = run_async(orchestrator.run_review(
                topic=topic,
                max_papers=max_papers,
                max_full_text_papers=max_full_text_papers,
                relevance_threshold=relevance_threshold,
                save_results=True,
                output_dir=app.config["OUTPUT_DIR"]
            ))
            
            # Store results in session
            session['topic'] = topic
            session['review_file'] = results['saved_files'].get('review_file')
            session['papers_file'] = results['saved_files'].get('papers_file')
            
            return redirect(url_for('results'))
        
        except Exception as e:
            flash(f'Error: {str(e)}', 'error')
            return redirect(url_for('index'))
    
    # GET request - show form
    return render_template('review_form.html')

@app.route('/results')
def results():
    """Show literature review results."""
    # Get results from session
    topic = session.get('topic')
    review_file = session.get('review_file')
    papers_file = session.get('papers_file')
    
    if not topic or not review_file:
        flash('No results found. Please start a new review.', 'error')
        return redirect(url_for('index'))
    
    # Load literature review from file
    try:
        with open(review_file, 'r', encoding='utf-8') as f:
            literature_review = f.read()
        
        # Load papers from file
        papers = []
        if papers_file and os.path.exists(papers_file):
            try:
                with open(papers_file, 'r', encoding='utf-8') as f:
                    papers_data = json.load(f)
                    if isinstance(papers_data, list):
                        papers = papers_data
                    elif isinstance(papers_data, dict) and 'papers' in papers_data:
                        papers = papers_data['papers']
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Error loading papers: {e}")
                papers = []
        
        return render_template('results.html', 
                               topic=topic, 
                               literature_review=literature_review, 
                               papers=papers)
    
    except Exception as e:
        flash(f'Error loading results: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')

if __name__ == '__main__':
    # First, check if Ollama is accessible
    print(f"Checking Ollama connection at {ollama_url}...")
    try:
        test_response = llm.invoke("test")
        print("✅ Ollama is connected and working!")
    except Exception as e:
        print(f"⚠️ Warning: Could not connect to Ollama: {e}")
        print("Make sure Ollama is running with: ollama serve")
    
    app.run(host='0.0.0.0', port=5000, debug=True)