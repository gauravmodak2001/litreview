import os
import asyncio
import json
import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import re
from pathlib import Path
from browser_use import Agent
from langchain_ollama import ChatOllama

# Define paper structure
@dataclass
class Paper:
    title: str
    authors: List[str]
    abstract: str
    url: str
    year: Optional[int] = None
    venue: Optional[str] = None
    citations: Optional[int] = None
    keywords: List[str] = field(default_factory=list)
    full_text: Optional[str] = None
    relevance_score: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title,
            "authors": self.authors,
            "abstract": self.abstract,
            "url": self.url,
            "year": self.year,
            "venue": self.venue,
            "citations": self.citations,
            "keywords": self.keywords,
            "full_text": self.full_text,
            "relevance_score": self.relevance_score
        }


class SearchAgent:
    """Agent responsible for searching papers across multiple sources"""
    def __init__(self, llm):
        self.llm = llm
        
    async def search(self, topic: str, max_papers: int = 15) -> List[Paper]:
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
        
        # Extract paper information from the result
        papers_data = self._extract_paper_data(result)
        
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


class ContentRetrievalAgent:
    """Agent responsible for retrieving full text or additional information for papers"""
    def __init__(self, llm):
        self.llm = llm
        
    async def retrieve_content(self, paper: Paper) -> Paper:
        """Retrieve full content and additional details for a paper"""
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
        
        # Update the paper with additional information
        paper.full_text = result.strip()
        
        # Try to extract keywords from the result
        keywords_match = re.search(r'Keywords:\s*(.*?)(?:\n|$)', result, re.IGNORECASE)
        if keywords_match:
            keywords_text = keywords_match.group(1)
            paper.keywords = [kw.strip() for kw in re.split(r',|;', keywords_text) if kw.strip()]
        
        # Try to extract citation count
        citations_match = re.search(r'Citations:\s*(\d+)', result, re.IGNORECASE)
        if citations_match:
            try:
                paper.citations = int(citations_match.group(1))
            except ValueError:
                pass
            
        return paper


class FilterAgent:
    """Agent responsible for filtering papers based on relevance to the topic"""
    def __init__(self, llm):
        self.llm = llm
        
    async def filter_papers(self, papers: List[Paper], topic: str, relevance_threshold: float = 0.7) -> List[Paper]:
        """Filter papers based on relevance and assign relevance scores"""
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
            
            # Extract the relevance score
            score_match = re.search(r'RELEVANCE_SCORE:\s*(\d+\.\d+)', result)
            if score_match:
                relevance_score = float(score_match.group(1))
            else:
                # Fallback pattern
                score_match = re.search(r'(\d+\.\d+)', result)
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


class SummaryAgent:
    """Agent responsible for summarizing papers and generating a literature review"""
    def __init__(self, llm):
        self.llm = llm
        
    async def generate_literature_review(self, papers: List[Paper], topic: str) -> str:
        """Generate a comprehensive literature review from the papers"""
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
                
                Content:
                {content[:5000]}  # Limit to avoid token issues
                
                Provide a concise summary (150-200 words) covering:
                1. The main research question or objective
                2. Methodology used
                3. Key findings
                4. Implications or conclusions
                """,
                llm=self.llm,
                max_actions_per_step=2,
            )
            
            summary = await agent.run(max_steps=5)
            paper_summaries.append((paper, summary))
        
        # Create a comprehensive literature review
        papers_info = "\n\n".join([
            f"Paper {i+1}:\nTitle: {paper.title}\nAuthors: {', '.join(paper.authors)}\nYear: {paper.year if paper.year else 'Unknown'}\nRelevance: {paper.relevance_score:.2f}\nSummary: {summary}"
            for i, (paper, summary) in enumerate(paper_summaries)
        ])
        
        # Generate the literature review
        agent = Agent(
            task=f"""
            Generate a comprehensive literature review on the topic of '{topic}' based on the following papers:
            
            {papers_info}
            
            The literature review should include:
            1. An introduction to the topic and its importance
            2. An overview of the current state of research
            3. A synthesis of the main findings and themes across the papers
            4. Identification of gaps in the literature
            5. Suggestions for future research directions
            6. A conclusion
            
            Format the literature review with appropriate sections and subsections.
            """,
            llm=self.llm,
            max_actions_per_step=3,
        )
        
        literature_review = await agent.run(max_steps=10)
        return literature_review


class LiteratureReviewSystem:
    """Main system for conducting a literature review"""
    def __init__(self, model_name="stablelm-zephyr:3b", output_dir="literature_review_output"):
        self.llm = ChatOllama(
            model=model_name,
            num_ctx=32000,
        )
        
        self.search_agent = SearchAgent(self.llm)
        self.content_agent = ContentRetrievalAgent(self.llm)
        self.filter_agent = FilterAgent(self.llm)
        self.summary_agent = SummaryAgent(self.llm)
        
        # Create output directory if it doesn't exist
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    async def run_literature_review(self, topic: str, max_papers: int = 10, relevance_threshold: float = 0.7):
        """Run the full literature review pipeline"""
        print(f"Starting literature review on '{topic}'")
        
        # Step 1: Search for papers
        print("\nStep 1: Searching for papers...")
        papers = await self.search_agent.search(topic, max_papers)
        print(f"Found {len(papers)} papers")
        
        # Step 2: Filter papers based on relevance
        print("\nStep 2: Filtering papers based on relevance...")
        filtered_papers = await self.filter_agent.filter_papers(papers, topic, relevance_threshold)
        print(f"Kept {len(filtered_papers)} relevant papers")
        
        # Step 3: Retrieve full content for relevant papers
        print("\nStep 3: Retrieving full content for relevant papers...")
        papers_with_content = []
        for i, paper in enumerate(filtered_papers):
            print(f"Retrieving content for paper {i+1}/{len(filtered_papers)}: '{paper.title}'...")
            paper_with_content = await self.content_agent.retrieve_content(paper)
            papers_with_content.append(paper_with_content)
            
        # Step 4: Generate literature review
        print("\nStep 4: Generating literature review...")
        literature_review = await self.summary_agent.generate_literature_review(papers_with_content, topic)
        
        # Step 5: Save all results
        print("\nStep 5: Saving results...")
        self._save_results(topic, papers_with_content, literature_review)
        
        return literature_review
    
    def _save_results(self, topic: str, papers: List[Paper], literature_review: str):
        """Save all results to the output directory"""
        # Create a topic-specific directory
        safe_topic = re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '_')
        topic_dir = self.output_dir / safe_topic
        topic_dir.mkdir(exist_ok=True)
        
        # Save each paper as a JSON file and full text
        papers_dir = topic_dir / "papers"
        papers_dir.mkdir(exist_ok=True)
        
        for i, paper in enumerate(papers):
            # Create a safe filename based on the paper title
            safe_title = re.sub(r'[^\w\s-]', '', paper.title).strip().replace(' ', '_')
            if len(safe_title) > 50:
                safe_title = safe_title[:50]
            
            # Save paper metadata as JSON
            paper_path = papers_dir / f"{i+1}_{safe_title}.json"
            with open(paper_path, 'w', encoding='utf-8') as f:
                json.dump(paper.to_dict(), f, indent=2)
                
            # Save full text as a separate file if available
            if paper.full_text:
                text_path = papers_dir / f"{i+1}_{safe_title}.txt"
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {paper.title}\n")
                    f.write(f"Authors: {', '.join(paper.authors)}\n")
                    if paper.year:
                        f.write(f"Year: {paper.year}\n")
                    if paper.venue:
                        f.write(f"Venue: {paper.venue}\n")
                    f.write(f"URL: {paper.url}\n")
                    if paper.keywords:
                        f.write(f"Keywords: {', '.join(paper.keywords)}\n")
                    f.write("\n")
                    f.write(paper.full_text)
        
        # Save the literature review as a markdown file
        review_path = topic_dir / "literature_review.md"
        with open(review_path, 'w', encoding='utf-8') as f:
            f.write(f"# Literature Review: {topic}\n\n")
            f.write(f"Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(literature_review)
        
        # Save a metadata file with information about the review
        metadata = {
            "topic": topic,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "papers_found": len(papers),
            "papers": [
                {
                    "title": p.title,
                    "authors": p.authors,
                    "year": p.year,
                    "venue": p.venue,
                    "relevance_score": p.relevance_score,
                    "url": p.url
                } for p in papers
            ]
        }
        
        metadata_path = topic_dir / "metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
            
        print(f"Results saved to {topic_dir}")


async def main():
    """Main function to run the literature review system"""
    # Get the topic from the user
    topic = input("Enter the literature review topic: ")
    
    # Get optional parameters with defaults
    try:
        max_papers = int(input("Enter the maximum number of papers to search for (default: 10): ").strip() or "10")
    except ValueError:
        max_papers = 10
        
    try:
        relevance_threshold = float(input("Enter the relevance threshold (0.0-1.0, default: 0.7): ").strip() or "0.7")
        if relevance_threshold < 0 or relevance_threshold > 1:
            print("Invalid threshold, using default of 0.7")
            relevance_threshold = 0.7
    except ValueError:
        relevance_threshold = 0.7
    
    # Create and run the literature review system
    print(f"\nInitializing literature review system for topic: '{topic}'")
    print(f"Max papers: {max_papers}, Relevance threshold: {relevance_threshold}")
    
    system = LiteratureReviewSystem()
    literature_review = await system.run_literature_review(
        topic=topic,
        max_papers=max_papers,
        relevance_threshold=relevance_threshold
    )
    
    print("\nLiterature review completed!")
    print(f"The results have been saved to the 'literature_review_output/{re.sub(r'[^\w\s-]', '', topic).strip().replace(' ', '_')}' directory.")
    
    # Print a short preview of the literature review
    preview_length = min(500, len(literature_review))
    print(f"\nPreview of the literature review:\n{literature_review[:preview_length]}...\n")


if __name__ == "__main__":
    asyncio.run(main())