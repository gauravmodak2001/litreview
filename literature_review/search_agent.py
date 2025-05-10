"""
Search agent module for finding academic papers across various sources.
"""

import json
import re
from typing import List, Dict, Any
from browser_use import Agent

from literature_review.models import Paper
from literature_review.utils_browser import convert_agent_result_to_string

class SearchAgent:
    """Agent responsible for searching papers across multiple sources"""
    def __init__(self, llm):
        self.llm = llm
        
    async def search(self, topic: str, max_papers: int = 15) -> List[Paper]:
        """
        Search for academic papers on a given topic.
        
        Args:
            topic: The research topic to search for
            max_papers: Maximum number of papers to return
            
        Returns:
            List of Paper objects with basic metadata
        """
        # Create a browser agent to search across multiple academic databases
        agent = Agent(
            task=f"""Find the most relevant and recent academic papers about '{topic}'. 
            Search across Google Scholar, arXiv, ResearchGate, and other academic databases.
            For each paper, extract the title, authors, abstract, publication year, venue/journal, and URL.
            Focus on papers published in the last 5 years if possible.
            Format the results as a JSON list where each paper is an object with keys: 
            title, authors (as a list), abstract, year, venue, and url.
            Return at least {max_papers} papers if available.""",
            llm=self.llm,
            max_actions_per_step=5,
        )
        
        result = await agent.run(max_steps=15)
        
        # Convert result to string using our utility function
        result_text = convert_agent_result_to_string(result)
            
        # Extract paper information from the result
        papers_data = self._extract_paper_data(result_text)
        
        # Convert to Paper objects
        papers = []
        for paper_data in papers_data:
            papers.append(Paper(
                title=paper_data.get("title", "Unknown Title"),
                authors=paper_data.get("authors", []),
                abstract=paper_data.get("abstract", ""),
                url=paper_data.get("url", ""),
                year=paper_data.get("year"),
                venue=paper_data.get("venue")
            ))
                
        return papers
    
    def _extract_paper_data(self, text: str) -> List[Dict[str, Any]]:
        """Extract paper data from the agent's response"""
        # Try to find a JSON structure in the text
        json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if json_match:
            try:
                papers_data = json.loads(json_match.group(1))
                if isinstance(papers_data, list):
                    return papers_data
            except json.JSONDecodeError:
                pass
        
        # Try to find any JSON-like structure
        papers_data_match = re.search(r'\[\s*\{[\s\S]*\}\s*\]', text)
        if papers_data_match:
            try:
                papers_data = json.loads(papers_data_match.group(0))
                if isinstance(papers_data, list):
                    return papers_data
            except json.JSONDecodeError:
                pass
        
        # Fallback to manual extraction
        return self._manual_extraction(text)
    
    def _manual_extraction(self, text: str) -> List[Dict[str, Any]]:
        """Manually extract paper information from text"""
        papers = []
        
        # Split by potential paper entries (numbered list items or double newlines)
        entries = re.split(r'\d+\.\s+|\n\n+', text)
        
        for entry in entries:
            if not entry.strip():
                continue
                
            # Extract title (first line or after "Title:")
            title_match = re.search(r'(?:Title:\s*)(.*?)(?:\n|$)', entry, re.IGNORECASE)
            if title_match:
                title = title_match.group(1).strip()
            else:
                lines = entry.split('\n')
                title = lines[0].strip()
                if not title or len(title) > 200:  # Likely not a title
                    continue
            
            # Extract authors
            authors_match = re.search(r'(?:Authors?:\s*)(.*?)(?:\n|$)', entry, re.IGNORECASE)
            if authors_match:
                authors_text = authors_match.group(1)
                authors = [author.strip() for author in re.split(r',|\band\b|;', authors_text) if author.strip()]
            else:
                authors = []
            
            # Extract abstract
            abstract_match = re.search(r'(?:Abstract:\s*)(.*?)(?:\n\n|\n[A-Z]|$)', entry, re.DOTALL | re.IGNORECASE)
            if abstract_match:
                abstract = abstract_match.group(1).strip()
            else:
                abstract = ""
            
            # Extract URL
            url_match = re.search(r'(?:URL|Link):\s*(https?://\S+)', entry, re.IGNORECASE)
            if url_match:
                url = url_match.group(1).strip()
            else:
                # Try to find any URL
                url_match = re.search(r'(https?://\S+)', entry)
                if url_match:
                    url = url_match.group(1).strip()
                else:
                    url = ""
            
            # Extract year
            year_match = re.search(r'(?:Year|Published):\s*(\d{4})', entry, re.IGNORECASE)
            if year_match:
                try:
                    year = int(year_match.group(1))
                except ValueError:
                    year = None
            else:
                # Try to find any 4-digit year
                year_match = re.search(r'\b(20\d{2}|19\d{2})\b', entry)
                if year_match:
                    try:
                        year = int(year_match.group(1))
                    except ValueError:
                        year = None
                else:
                    year = None
            
            # Extract venue
            venue_match = re.search(r'(?:Venue|Journal|Conference|Published in):\s*(.*?)(?:\n|$)', entry, re.IGNORECASE)
            if venue_match:
                venue = venue_match.group(1).strip()
            else:
                venue = None
            
            if title:  # Only add if we have a title
                papers.append({
                    "title": title,
                    "authors": authors,
                    "abstract": abstract,
                    "url": url,
                    "year": year,
                    "venue": venue
                })
        
        return papers
