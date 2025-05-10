"""
Module providing mock data for demonstration purposes when Ollama is not available.
"""

import asyncio
import json
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional

from literature_review.models import Paper

# Sample mock papers data
MOCK_PAPERS = [
    {
        "title": "The Ethics of Artificial Intelligence: Current Landscape and Future Directions",
        "authors": ["Smith, J.", "Johnson, A.", "Williams, R."],
        "abstract": "This paper provides a comprehensive overview of ethical considerations in artificial intelligence development and deployment, examining issues of bias, transparency, accountability, and privacy. We analyze existing frameworks and propose new directions for ethical AI governance.",
        "url": "https://example.com/ethics-ai-paper1",
        "year": 2023,
        "venue": "Journal of AI Ethics",
        "citations": 42,
        "keywords": ["AI ethics", "algorithmic bias", "fairness", "transparency"],
        "relevance_score": 0.95
    },
    {
        "title": "Fairness and Accountability in Machine Learning Systems",
        "authors": ["Garcia, M.", "Chen, L."],
        "abstract": "We examine how fairness and accountability principles can be incorporated into machine learning systems. This paper presents a framework for evaluating algorithmic fairness across different contexts and proposes methods for ensuring accountability in automated decision-making.",
        "url": "https://example.com/fairness-ml-paper",
        "year": 2022,
        "venue": "Conference on Fairness, Accountability, and Transparency",
        "citations": 87,
        "keywords": ["fairness", "accountability", "machine learning", "ethics"],
        "relevance_score": 0.88
    },
    {
        "title": "AI Bias Mitigation: Techniques and Challenges",
        "authors": ["Taylor, S.", "Patel, K.", "Nguyen, H."],
        "abstract": "This research examines various techniques for mitigating bias in AI systems and highlights ongoing challenges in this area. We evaluate several debiasing methods across different domains and propose a new framework for bias detection and mitigation.",
        "url": "https://example.com/ai-bias-paper",
        "year": 2021,
        "venue": "AI and Society Journal",
        "citations": 63,
        "keywords": ["AI bias", "fairness", "debiasing", "ethical AI"],
        "relevance_score": 0.86
    },
    {
        "title": "Privacy-Preserving Machine Learning: An Ethical Perspective",
        "authors": ["Brown, D.", "Lee, E."],
        "abstract": "We address the intersection of privacy concerns and machine learning, examining how privacy-preserving techniques align with ethical principles. The paper proposes a framework for evaluating the ethical implications of privacy mechanisms in AI systems.",
        "url": "https://example.com/privacy-ml-ethics",
        "year": 2023,
        "venue": "International Journal of Data Privacy",
        "citations": 29,
        "keywords": ["privacy", "machine learning", "ethics", "data protection"],
        "relevance_score": 0.82
    },
    {
        "title": "Responsible AI Development in Healthcare",
        "authors": ["Miller, J.", "Wilson, T.", "Khan, S."],
        "abstract": "This paper examines ethical considerations specific to AI applications in healthcare. We analyze case studies across diagnosis, treatment planning, and patient monitoring, proposing guidelines for responsible AI deployment in medical contexts.",
        "url": "https://example.com/healthcare-ai-ethics",
        "year": 2022,
        "venue": "Healthcare Ethics and AI Symposium",
        "citations": 54,
        "keywords": ["healthcare AI", "medical ethics", "responsible AI", "patient privacy"],
        "relevance_score": 0.79
    }
]

MOCK_LITERATURE_REVIEW = """
# Literature Review: Artificial Intelligence Ethics

## Introduction

The rapid advancement of artificial intelligence (AI) technologies has raised numerous ethical concerns regarding their development, deployment, and governance. This literature review examines the current landscape of AI ethics research, focusing on key themes including fairness, accountability, transparency, privacy, and domain-specific ethical considerations.

## Major Themes and Findings

### Fairness and Bias in AI

Multiple studies have identified algorithmic bias as a critical ethical concern in AI systems. Smith et al. (2023) provide a comprehensive overview of bias manifestations across various AI applications, noting that biases can emerge from training data, algorithm design, and implementation contexts. Garcia and Chen (2022) propose a framework for evaluating algorithmic fairness that considers multiple dimensions including group fairness, individual fairness, and counterfactual fairness.

Taylor et al. (2021) evaluate several bias mitigation techniques, finding that pre-processing methods showed particular promise for addressing demographic biases, while in-processing techniques were more effective for handling representation biases. Their work highlights the importance of context-specific approaches to bias mitigation, as no single solution proved effective across all domains and applications.

### Transparency and Accountability

Transparency and accountability emerge as interconnected ethical principles critical to responsible AI. Garcia and Chen (2022) argue that transparency must extend beyond mere technical explainability to include meaningful disclosure about system capabilities, limitations, and potential impacts. Their framework for accountability incorporates both procedural elements (documentation, testing, monitoring) and substantive measures (redress mechanisms, liability assignment).

Smith et al. (2023) emphasize the tension between calls for complete algorithmic transparency and concerns about intellectual property protection and security vulnerabilities. They propose a tiered transparency approach that balances stakeholder needs for information against legitimate business interests.

### Privacy and Data Ethics

Privacy concerns intersect significantly with AI ethics, as highlighted by Brown and Lee (2023). Their research examines the relationship between privacy-preserving machine learning techniques and broader ethical principles, noting that differential privacy approaches often involve explicit trade-offs between utility and privacy protection. They propose an evaluation framework that considers both technical privacy guarantees and social-contextual factors in determining appropriate privacy protections.

### Domain-Specific Ethical Considerations

Several studies emphasize the importance of domain-specific ethical analysis. Miller et al. (2022) examine AI applications in healthcare, identifying unique ethical considerations related to patient autonomy, informed consent, and the potential disruption of doctor-patient relationships. Their case studies across diagnosis, treatment planning, and patient monitoring reveal that ethical requirements vary significantly by application context, suggesting the need for specialized ethical frameworks rather than one-size-fits-all approaches.

## Research Methodologies

The reviewed literature employs diverse methodologies to address AI ethics questions. Theoretical frameworks and conceptual analyses predominate, particularly in papers addressing broad ethical principles (Smith et al., 2023; Garcia & Chen, 2022). Case study approaches are common in domain-specific investigations (Miller et al., 2022), while empirical evaluations of bias and fairness often utilize statistical analyses of system performance across demographic groups (Taylor et al., 2021).

Notable methodological gaps include limited longitudinal studies examining the ethical implications of AI systems over time and few participatory research approaches that incorporate perspectives from affected communities.

## Research Gaps and Future Directions

Several research gaps emerge from this literature review. First, while considerable attention has been paid to bias and fairness concerns, less research addresses the potential tension between different ethical principles, such as cases where transparency might compromise privacy or security. Second, most ethical frameworks remain theoretical, with limited practical implementation guidance for developers and deployers of AI systems.

Future research directions should include:

1. Development of practical tools and methodologies for ethical impact assessment
2. Longitudinal studies tracking ethical implications of AI systems over time
3. Cross-cultural examinations of AI ethics to account for global value differences
4. Integration of affected community perspectives in AI ethics research

## Conclusion

The literature on AI ethics reveals a complex landscape of interconnected concerns across fairness, accountability, transparency, and privacy domains. While significant theoretical work has established key principles and frameworks, practical implementation guidance remains limited. Domain-specific ethical analysis appears essential, as ethical requirements vary substantially by application context. Future research should focus on developing practical tools for ethical assessment, conducting longitudinal studies, and incorporating diverse perspectives from affected communities.

## References

Brown, D., & Lee, E. (2023). Privacy-Preserving Machine Learning: An Ethical Perspective. International Journal of Data Privacy.

Garcia, M., & Chen, L. (2022). Fairness and Accountability in Machine Learning Systems. Conference on Fairness, Accountability, and Transparency.

Miller, J., Wilson, T., & Khan, S. (2022). Responsible AI Development in Healthcare. Healthcare Ethics and AI Symposium.

Smith, J., Johnson, A., & Williams, R. (2023). The Ethics of Artificial Intelligence: Current Landscape and Future Directions. Journal of AI Ethics.

Taylor, S., Patel, K., & Nguyen, H. (2021). AI Bias Mitigation: Techniques and Challenges. AI and Society Journal.
"""

async def get_mock_papers(topic: str = "artificial intelligence ethics") -> List[Paper]:
    """Return a list of mock Paper objects for demonstration purposes."""
    papers = []
    for paper_data in MOCK_PAPERS:
        papers.append(Paper(
            title=paper_data["title"],
            authors=paper_data["authors"],
            abstract=paper_data["abstract"],
            url=paper_data["url"],
            year=paper_data["year"],
            venue=paper_data["venue"],
            citations=paper_data.get("citations"),
            keywords=paper_data.get("keywords", []),
            relevance_score=paper_data.get("relevance_score", 0.8)
        ))
    
    # Simulate some processing time for realism
    await asyncio.sleep(2)
    return papers

async def get_mock_literature_review(topic: str = "artificial intelligence ethics") -> str:
    """Return a mock literature review for demonstration purposes."""
    # Simulate processing time for realism
    await asyncio.sleep(3)
    return MOCK_LITERATURE_REVIEW

async def save_mock_results(topic: str, papers: List[Paper], literature_review: str, output_dir: str = 'output') -> Dict[str, str]:
    """Save mock results to files."""
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
    
    # Simulate some processing time
    await asyncio.sleep(1)
    
    return {
        "papers_file": str(papers_file),
        "review_file": str(review_file)
    }