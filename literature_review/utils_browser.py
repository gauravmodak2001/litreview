"""
Utility functions for working with browser-use Agent results.
"""

def convert_agent_result_to_string(result):
    """
    Convert the result from browser-use Agent.run() to a string, regardless of its type.
    
    Args:
        result: Result from agent.run(), which could be a string or AgentHistoryList
        
    Returns:
        String representation of the result
    """
    # Check if the result is an instance of AgentHistoryList from browser-use
    if hasattr(result, '__class__') and hasattr(result.__class__, '__name__') and result.__class__.__name__ == 'AgentHistoryList':
        # Try different methods to extract the content as string
        if hasattr(result, '__str__'):
            return str(result)
        elif hasattr(result, 'to_string'):
            return result.to_string()
        elif hasattr(result, 'text'):
            return result.text
        elif hasattr(result, 'content'):
            return result.content
        elif hasattr(result, '__iter__'):
            # If it's iterable, try to join the contents
            try:
                return "\n".join(str(item) for item in result)
            except Exception:
                pass
    
    # Default fallback - convert to string
    return str(result)