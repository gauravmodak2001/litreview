"""
Mock orchestrator module for demonstration purposes when Ollama is not available.
"""

import asyncio
from typing import Dict, Any, List

from literature_review.models import Paper
from literature_review.mock_data import get_mock_papers, get_mock_literature_review, save_mock_results

class MockLiteratureReviewOrchestrator:
    """Mock version of LiteratureReviewOrchestrator for demonstration without Ollama"""
    
    def __init__(self, *args, **kwargs):
        """Initialize the mock orchestrator, ignoring any arguments."""
        pass
    
    async def run_review(self, 
                       topic: str, 
                       max_papers: int = 15, 
                       max_full_text_papers: int = 10,
                       relevance_threshold: float = 0.7,
                       save_results: bool = True,
                       output_dir: str = 'output') -> Dict[str, Any]:
        """
        Run a mock literature review process with predefined results.
        
        Args:
            topic: Research topic to review
            max_papers: Maximum number of papers to initially search for (ignored in mock)
            max_full_text_papers: Maximum number of papers to retrieve full text for (ignored in mock)
            relevance_threshold: Minimum relevance score (0.0-1.0) to keep a paper (ignored in mock)
            save_results: Whether to save results to files
            output_dir: Directory to save output files
            
        Returns:
            Dictionary with papers and literature review
        """
        print(f"🔍 Searching for papers on: {topic} (DEMO MODE)")
        papers = await get_mock_papers(topic)
        print(f"📚 Found {len(papers)} papers (DEMO MODE)")
        
        # Simulate retrieving full text for papers
        print(f"📄 Retrieving full text for papers (DEMO MODE)")
        await asyncio.sleep(3)  # Simulate processing time
        
        # Simulate filtering papers by relevance
        print(f"🔍 Filtering papers by relevance (DEMO MODE)")
        filtered_papers = papers
        print(f"✅ Filtered to {len(filtered_papers)} relevant papers (DEMO MODE)")
        
        # Generate mock literature review
        print(f"📝 Generating literature review (DEMO MODE)")
        literature_review = await get_mock_literature_review(topic)
        
        # Save results if requested
        saved_files = {}
        if save_results:
            print(f"💾 Saving results to {output_dir} (DEMO MODE)")
            saved_files = await save_mock_results(
                topic, filtered_papers, literature_review, output_dir
            )
            print(f"📂 Saved papers to: {saved_files.get('papers_file')}")
            print(f"📄 Saved review to: {saved_files.get('review_file')}")
        
        return {
            "topic": topic,
            "papers": filtered_papers,
            "literature_review": literature_review,
            "saved_files": saved_files,
            "demo_mode": True
        }