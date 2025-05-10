"""
Automated Literature Review Package

A modular Python system for automated literature reviews that searches,
retrieves, filters, and summarizes academic papers.
"""

from literature_review.models import Paper
from literature_review.search_agent import SearchAgent
from literature_review.content_agent import ContentRetrievalAgent
from literature_review.filter_agent import FilterAgent  
from literature_review.summary_agent import SummaryAgent
from literature_review.review_orchestrator import LiteratureReviewOrchestrator

__all__ = [
    'Paper',
    'SearchAgent',
    'ContentRetrievalAgent',
    'FilterAgent',
    'SummaryAgent',
    'LiteratureReviewOrchestrator',
]
