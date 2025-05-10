"""
Utility functions for the literature review system.
"""

import os
import json
from typing import List, Dict, Any
from pathlib import Path
import datetime

from literature_review.models import Paper

def save_review_data(papers: List[Paper], literature_review: str, topic: str, output_dir: str = 'output') -> Dict[str, str]:
    """
    Save literature review results to files.
    
    Args:
        papers: List of Paper objects
        literature_review: Generated literature review text
        topic: Research topic
        output_dir: Directory to save output files
        
    Returns:
        Dictionary with paths to saved files
    """
    # Create timestamp for filenames
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create output directory if it doesn't exist
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Sanitize topic for filename
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic)
    safe_topic = safe_topic[:50]  # Limit length
    
    # Save papers data as JSON
    papers_file = output_path / f"papers_{safe_topic}_{timestamp}.json"
    with open(papers_file, 'w', encoding='utf-8') as f:
        json.dump([paper.to_dict() for paper in papers], f, indent=2)
    
    # Save literature review as text
    review_file = output_path / f"review_{safe_topic}_{timestamp}.md"
    with open(review_file, 'w', encoding='utf-8') as f:
        f.write(f"# Literature Review: {topic}\n\n")
        f.write(f"*Generated on: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n")
        f.write(literature_review)
    
    return {
        "papers_file": str(papers_file),
        "review_file": str(review_file)
    }

def load_papers(file_path: str) -> List[Paper]:
    """
    Load papers from a JSON file.
    
    Args:
        file_path: Path to JSON file containing paper data
        
    Returns:
        List of Paper objects
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        papers_data = json.load(f)
    
    papers = []
    for paper_data in papers_data:
        paper = Paper(
            title=paper_data.get("title", "Unknown Title"),
            authors=paper_data.get("authors", []),
            abstract=paper_data.get("abstract", ""),
            url=paper_data.get("url", ""),
            year=paper_data.get("year"),
            venue=paper_data.get("venue"),
            citations=paper_data.get("citations"),
            keywords=paper_data.get("keywords", []),
            full_text=paper_data.get("full_text"),
            relevance_score=paper_data.get("relevance_score", 0.0)
        )
        papers.append(paper)
    
    return papers
