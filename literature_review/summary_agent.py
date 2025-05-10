"""
Summary agent module for generating paper summaries and literature reviews.
"""

import re
from typing import List, Dict, Any
from browser_use import Agent

from literature_review.models import Paper
from literature_review.utils_browser import convert_agent_result_to_string

class SummaryAgent:
    """Agent responsible for summarizing papers and generating a literature review"""
    def __init__(self, llm):
        self.llm = llm
        
    async def generate_literature_review(self, papers: List[Paper], topic: str) -> str:
        """
        Generate a comprehensive literature review from the papers.
        
        Args:
            papers: List of Paper objects to include in review
            topic: The research topic of the literature review
            
        Returns:
            String containing formatted literature review
        """
        # Prepare paper summaries
        paper_summaries = []
        
        for i, paper in enumerate(papers):
            print(f"Summarizing paper {i+1}/{len(papers)}: {paper.title}")
            
            # Determine content to use for summary
            content = paper.full_text if paper.full_text else paper.abstract
            
            # Create an agent to summarize the paper
            agent = Agent(
                task=f"""
                Summarize the following paper:
                
                Title: {paper.title}
                Authors: {', '.join(paper.authors)}
                Year: {paper.year if paper.year else 'Unknown'}
                Venue: {paper.venue if paper.venue else 'Unknown'}
                
                Content:
                {content[:5000]}  # Limit content length
                
                Provide a concise summary (200-300 words) that covers:
                1. Main research question/objective
                2. Methodology/approach
                3. Key findings/results
                4. Implications/conclusions
                """,
                llm=self.llm,
                max_actions_per_step=3,
            )
            
            result = await agent.run(max_steps=5)
            
            # Convert result to string using our utility function
            summary = convert_agent_result_to_string(result)
            
            # Add to list of paper summaries
            paper_summaries.append({
                "title": paper.title,
                "authors": paper.authors,
                "year": paper.year,
                "venue": paper.venue,
                "summary": summary,
                "relevance_score": paper.relevance_score
            })
        
        # Generate literature review from paper summaries
        review_agent = Agent(
            task=f"""
            Generate a comprehensive literature review on the topic: '{topic}'
            
            Use the following {len(paper_summaries)} papers as sources:
            
            {self._format_papers_for_review(paper_summaries)}
            
            The literature review should include:
            
            1. Introduction to the topic and its importance
            2. Overview of major themes and findings in the literature
            3. Analysis of research methodologies used
            4. Synthesis of key findings and their implications
            5. Identification of research gaps and future directions
            6. Conclusion
            
            Format the literature review in a scholarly manner with proper sections and citations.
            Use in-text citations in the format (Author et al., Year) when referring to specific papers.
            Include a references section at the end listing all the papers.
            """,
            llm=self.llm,
            max_actions_per_step=5,
        )
        
        result = await review_agent.run(max_steps=10)
        
        # Convert result to string using our utility function
        literature_review = convert_agent_result_to_string(result)
        
        return literature_review
    
    def _format_papers_for_review(self, paper_summaries: List[Dict[str, Any]]) -> str:
        """Format paper summaries for input to the review generation prompt"""
        formatted_papers = []
        
        for i, paper in enumerate(paper_summaries):
            formatted_paper = f"""
            Paper {i+1}:
            Title: {paper['title']}
            Authors: {', '.join(paper['authors'])}
            Year: {paper['year'] if paper['year'] else 'Unknown'}
            Venue: {paper['venue'] if paper['venue'] else 'Unknown'}
            Relevance: {paper['relevance_score']:.2f}/1.00
            
            Summary:
            {paper['summary']}
            """
            formatted_papers.append(formatted_paper)
        
        return "\n\n".join(formatted_papers)
