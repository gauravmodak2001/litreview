"""
Data models for the literature review system.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field

@dataclass
class Paper:
    """Data class representing an academic paper with all its metadata."""
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
        """Convert paper object to dictionary for serialization."""
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
