"""
Main script for running the Automated Literature Review System.

This module exposes the Flask app instance for Gunicorn to use.
It can also be run directly as a command-line tool for generating a literature review.

Usage:
    python main.py           # Run Flask app directly
    python main.py [topic]   # Run as CLI tool with the given topic
"""

import os
import sys
import asyncio
from langchain_ollama import ChatOllama

from literature_review import LiteratureReviewOrchestrator

# Import and expose the Flask app
from app import app

async def run_cli(topic):
    """Run as a command-line tool"""
    print(f"🔍 Starting literature review on topic: {topic}")
    
    try:
        # Try to use real orchestrator first
        try:
            # Initialize language model
            model_name = os.environ.get("LLM_MODEL", "llama2")
            llm = ChatOllama(model=model_name)
            
            # Create orchestrator
            orchestrator = LiteratureReviewOrchestrator(llm)
            demo_mode = False
            print("✅ Using real Ollama-based orchestrator")
        except Exception as e:
            # Fall back to mock orchestrator if Ollama is not available
            from literature_review.mock_orchestrator import MockLiteratureReviewOrchestrator
            orchestrator = MockLiteratureReviewOrchestrator()
            demo_mode = True
            print(f"⚠️ Using DEMO MODE with mock data (Error: {str(e)})")
        
        # Run literature review
        results = await orchestrator.run_review(
            topic=topic,
            max_papers=15,              # Maximum papers to search for
            max_full_text_papers=10,    # Maximum papers to retrieve full text for
            relevance_threshold=0.7,    # Minimum relevance score (0.0-1.0)
            save_results=True,          # Save results to files
            output_dir='output'         # Directory to save output files
        )
        
        # Print summary
        print("\n" + "="*80)
        if demo_mode:
            print(f"📚 Literature Review on '{topic}' completed! (DEMO MODE)")
        else:
            print(f"📚 Literature Review on '{topic}' completed!")
            
        print(f"📊 Found {len(results['papers'])} relevant papers")
        print(f"📄 Generated a literature review of {len(results['literature_review'].split())} words")
        
        if results['saved_files']:
            print(f"\n📂 Results saved to:")
            for file_type, file_path in results['saved_files'].items():
                print(f"  - {file_type}: {file_path}")
        
        print("\n✨ Review excerpt:")
        print("-"*80)
        # Print first 500 characters of the review
        print(results['literature_review'][:500] + "...")
        print("-"*80)
        
        return results
        
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

if __name__ == "__main__":
    # If a topic is provided as a command-line argument, run in CLI mode
    if len(sys.argv) > 1:
        topic = sys.argv[1]
        asyncio.run(run_cli(topic))
    else:
        # Otherwise, run as a Flask web app directly
        print("🚀 Starting Flask web application...")
        app.run(host='0.0.0.0', port=5000, debug=True)
