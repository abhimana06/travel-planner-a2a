from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
import httpx


def summarizer(state) -> str:
    """
    Generate summary report using LLM when conversation ends.

    Args:
        state: Current conversation state with messages

    Returns:
        Formatted summary string
    """
    messages = state.get("messages", [])

    if not messages:
        return "No conversation to summarize."

    # Extract conversation text
    conversation_text = ""
    for msg in messages:
        # Messages are now always dicts
        conversation_text += f"{msg.get('content', '')}\n"

    if not conversation_text.strip():
        return "No conversation content to summarize."

    # System prompt for summarization
    system_prompt = """You are summarizing a travel planning committee meeting for a Singapore trip.

Generate a comprehensive, well-structured summary that captures:

**DESTINATIONS & ATTRACTIONS:**
- List all proposed destinations mentioned
- Highlight recommended attractions and activities

**BUDGET ANALYSIS:**
- Total budget discussed
- Cost estimates and financial considerations
- Value-for-money recommendations

**ITINERARY PLANNING:**
- Proposed daily schedule or timeline
- Logistics and travel arrangements
- Duration of trip

**SOCIAL MEDIA & TRENDS:**
- Instagram-worthy spots mentioned
- Trending destinations suggested
- Photo opportunities highlighted

**COMMITTEE INSIGHTS:**
- Key recommendations from each member (Abhishek, Abhijit, Santhi, Govind)
- Specific expertise contributed

**DECISIONS & ACTION ITEMS:**
- Finalized decisions made
- Next steps to take
- Any unresolved questions

Format your summary with clear headers and bullet points.
Make it actionable and easy to reference for trip planning."""

    user_prompt = f"""Here's the travel planning discussion that took place:

{conversation_text}

Please provide a comprehensive summary of this travel planning committee meeting."""

    try:
        # Call LLM
        http_client = httpx.Client(verify=False)
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=1, http_client=http_client)

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])

        if isinstance(response.content, list):
            summary = " ".join(str(item) for item in response.content).strip()
        else:
            summary = str(response.content).strip()

        # Format with header
        return f"=== TRAVEL PLANNING COMMITTEE SUMMARY ===\n\n{summary}"

    except Exception as e:
        # Fallback to basic summary if LLM fails
        return f"""=== TRAVEL PLANNING COMMITTEE SUMMARY ===

Total messages: {len(messages)}

Unable to generate detailed summary at this time.
The planning discussion has been logged for review."""
