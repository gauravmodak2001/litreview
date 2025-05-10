"""
Content retrieval agent module for getting full text and additional details of papers.
"""

import re
from browser_use import Agent

from literature_review.models import Paper
from literature_review.utils_browser import convert_agent_result_to_string

class ContentRetrievalAgent:
    """Agent responsible for retrieving full text or additional information for papers"""
    def __init__(self, llm):
        self.llm = llm
        
    async def retrieve_content(self, paper: Paper) -> Paper:
        """
        Retrieve full content and additional details for a paper.
        
        Args:
            paper: Paper object to retrieve content for
            
        Returns:
            Updated Paper object with full text and additional metadata
        """
        if not paper.url:
            print(f"No URL available for '{paper.title}', skipping content retrieval")
            return paper
        
        # Create a browser agent to retrieve the full text and additional information
        agent = Agent(
            task=f"""
            Visit {paper.url} and extract the following information for the paper titled '{paper.title}':
            
            1. Full text of the paper if available (or as much as possible)
            2. Keywords or subject areas
            3. Citation count if shown
            
            If the full text is not accessible, extract as much information as possible including extended abstract, 
            introduction, methodology, results, and conclusion sections.
            """,
            llm=self.llm,
            max_actions_per_step=5,
        )
        
        result = await agent.run(max_steps=12)
        
        # Convert result to string using our utility function
        result_text = convert_agent_result_to_string(result)
            
        # Update the paper with additional information
        paper.full_text = result_text.strip()
        
        # Try to extract keywords from the result
        keywords_match = re.search(r'Keywords:\s*(.*?)(?:\n|$)', result_text, re.IGNORECASE)
        if keywords_match:
            keywords_text = keywords_match.group(1)
            paper.keywords = [kw.strip() for kw in re.split(r',|;', keywords_text) if kw.strip()]
        
        # Try to extract citation count
        citations_match = re.search(r'Citations:\s*(\d+)', result_text, re.IGNORECASE)
        if citations_match:
            try:
                paper.citations = int(citations_match.group(1))
            except ValueError:
                pass
            
        return paper
