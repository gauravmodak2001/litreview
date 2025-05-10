"""
Filter agent module for assessing and filtering papers based on relevance.
"""

import re
from typing import List
from browser_use import Agent

from literature_review.models import Paper
from literature_review.utils_browser import convert_agent_result_to_string

class FilterAgent:
    """Agent responsible for filtering papers based on relevance to the topic"""
    def __init__(self, llm):
        self.llm = llm
        
    async def filter_papers(self, papers: List[Paper], topic: str, relevance_threshold: float = 0.7) -> List[Paper]:
        """
        Filter papers based on relevance and assign relevance scores.
        
        Args:
            papers: List of Paper objects to filter
            topic: The research topic to assess relevance against
            relevance_threshold: Minimum relevance score (0.0-1.0) to keep a paper
            
        Returns:
            Filtered and sorted list of Paper objects
        """
        filtered_papers = []
        
        for paper in papers:
            # Prepare content for assessment
            content = f"""
            Title: {paper.title}
            Authors: {', '.join(paper.authors)}
            Abstract: {paper.abstract}
            """
            if paper.keywords:
                content += f"Keywords: {', '.join(paper.keywords)}\n"
            
            # Create an agent to assess relevance
            agent = Agent(
                task=f"""
                Assess how relevant the following paper is to the topic '{topic}' on a scale from 0.0 to 1.0.
                
                {content}
                
                Explain your assessment briefly, then on the last line provide just the numerical score in the format: RELEVANCE_SCORE: X.X
                """,
                llm=self.llm,
                max_actions_per_step=2,
            )
            
            result = await agent.run(max_steps=3)
            
            # Convert result to string using our utility function
            result_text = convert_agent_result_to_string(result)
            
            # Extract the relevance score
            score_match = re.search(r'RELEVANCE_SCORE:\s*(\d+\.\d+)', result_text)
            if score_match:
                relevance_score = float(score_match.group(1))
            else:
                # Fallback pattern
                score_match = re.search(r'(\d+\.\d+)', result_text)
                if score_match:
                    relevance_score = float(score_match.group(1))
                else:
                    relevance_score = 0.5  # Default moderate relevance
            
            # Update the paper's relevance score
            paper.relevance_score = relevance_score
            
            # Keep if above threshold
            if relevance_score >= relevance_threshold:
                filtered_papers.append(paper)
                print(f"Paper '{paper.title}' is relevant (score: {relevance_score:.2f})")
            else:
                print(f"Paper '{paper.title}' is not relevant enough (score: {relevance_score:.2f})")
        
        # Sort by relevance
        filtered_papers.sort(key=lambda p: p.relevance_score, reverse=True)
        return filtered_papers
