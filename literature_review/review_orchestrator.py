"""
Orchestrator module for coordinating the literature review process.
"""

import asyncio
from typing import List, Dict, Any, Optional
import os

from literature_review.models import Paper
from literature_review.search_agent import SearchAgent
from literature_review.content_agent import ContentRetrievalAgent
from literature_review.filter_agent import FilterAgent
from literature_review.summary_agent import SummaryAgent
from literature_review.utils import save_review_data

class LiteratureReviewOrchestrator:
    """Coordinates the entire literature review process"""
    
    def __init__(self, llm):
        """
        Initialize the orchestrator with agent instances.
        
        Args:
            llm: Language model instance to use for all agents
        """
        self.llm = llm
        self.search_agent = SearchAgent(llm)
        self.content_agent = ContentRetrievalAgent(llm)
        self.filter_agent = FilterAgent(llm)
        self.summary_agent = SummaryAgent(llm)
    
    async def run_review(self, 
                        topic: str, 
                        max_papers: int = 15, 
                        max_full_text_papers: int = 10,
                        relevance_threshold: float = 0.7,
                        save_results: bool = True,
                        output_dir: str = 'output') -> Dict[str, Any]:
        """
        Run the complete literature review process.
        
        Args:
            topic: Research topic to review
            max_papers: Maximum number of papers to initially search for
            max_full_text_papers: Maximum number of papers to retrieve full text for
            relevance_threshold: Minimum relevance score (0.0-1.0) to keep a paper
            save_results: Whether to save results to files
            output_dir: Directory to save output files
            
        Returns:
            Dictionary with papers and literature review
        """
        print(f"🔍 Searching for papers on: {topic}")
        papers = await self.search_agent.search(topic, max_papers)
        print(f"📚 Found {len(papers)} papers")
        
        # Retrieve full text for papers (limit to max_full_text_papers)
        print(f"📄 Retrieving full text for up to {max_full_text_papers} papers")
        papers_with_content = []
        for i, paper in enumerate(papers[:max_full_text_papers]):
            print(f"  📝 Retrieving content for paper {i+1}/{min(len(papers), max_full_text_papers)}: {paper.title}")
            paper_with_content = await self.content_agent.retrieve_content(paper)
            papers_with_content.append(paper_with_content)
        
        # Filter papers by relevance
        print(f"🔍 Filtering papers by relevance (threshold: {relevance_threshold})")
        filtered_papers = await self.filter_agent.filter_papers(
            papers_with_content, topic, relevance_threshold
        )
        print(f"✅ Filtered to {len(filtered_papers)} relevant papers")
        
        # Generate literature review
        print(f"📝 Generating literature review from {len(filtered_papers)} papers")
        literature_review = await self.summary_agent.generate_literature_review(
            filtered_papers, topic
        )
        
        # Save results if requested
        saved_files = {}
        if save_results:
            print(f"💾 Saving results to {output_dir}")
            saved_files = save_review_data(
                filtered_papers, literature_review, topic, output_dir
            )
            print(f"📂 Saved papers to: {saved_files.get('papers_file')}")
            print(f"📄 Saved review to: {saved_files.get('review_file')}")
        
        return {
            "topic": topic,
            "papers": filtered_papers,
            "literature_review": literature_review,
            "saved_files": saved_files
        }
