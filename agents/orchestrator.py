from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from utils import debug
import httpx


def orchestrator(state):
    """
    Select next speaker based on conversation context.
    Manages volley control and updates state accordingly.

    Updates state with:
    - next_speaker: Selected agent ID or "human"
    - volley_msg_left: Decremented counter

    Returns: Updated state
    """

    debug(state)
    volley_left = state.get("volley_msg_left", 0)
    debug(f"Volley messages left: {volley_left}", "ORCHESTRATOR")

    if volley_left <= 0:
        debug("No volleys left, returning to human", "ORCHESTRATOR")
        return {
            "next_speaker": "human",
            "volley_msg_left": 0
        }

    messages = state.get("messages", [])

    conversation_text = ""
    for msg in messages:
        # Messages are now always dicts
        conversation_text += f"{msg.get('content', '')}\n"

    system_prompt = """You are orchestrating a travel planning committee meeting.

    Available committee members:
    - abhishek: Adventurous traveler who wants to plan the trip, passionate about exploring new destinations
    - abhijit: Social media influencer, knows trending destinations and Instagram-worthy spots
    - santhi: Budget planning specialist, ensures trips stay within financial constraints
    - govind: Itinerary specialist with extensive travel planning experience

    Based on the planning discussion flow, select who should speak next to advance the travel planning effectively.
    Consider:
    - Who hasn't contributed recently
    - Who has relevant expertise for the current planning stage
    - Natural flow: abhishek initiates ideas → abhijit suggests trendy spots → santhi analyzes budget → govind creates detailed itinerary
    -abhijit should speak about social media trends and viral destinations
    - santhi should speak when budget or costs are discussed
    - govind should speak when detailed planning or logistics are needed

    Respond with ONLY the speaker ID (abhishek, abhijit, santhi, or govind).
    """

    user_prompt = f"""Recent travel planning discussion:
{conversation_text}

Who should speak next to advance this travel planning discussion?"""

    debug("Analyzing conversation context...", "ORCHESTRATOR")

    # Call LLM
    try:
        http_client = httpx.Client(verify=False)
        llm = ChatOpenAI(model="gpt-4o-mini", temperature=1, http_client=http_client)

        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt)
        ])

        # Extract speaker from response
        if isinstance(response.content, list):
            selected_speaker = " ".join(str(item) for item in response.content).strip().lower()
        else:
            selected_speaker = str(response.content).strip().lower()
        debug(f"LLM selected: {selected_speaker}", "ORCHESTRATOR")

        # Validate speaker
        valid_speakers = ["abhishek", "abhijit", "santhi", "govind"]
        if selected_speaker not in valid_speakers:
            # Fallback to round-robin if invalid
            import random
            selected_speaker = random.choice(valid_speakers)
            debug(f"Invalid speaker, fallback to: {selected_speaker}", "ORCHESTRATOR")

    except Exception as e:
        # Fallback selection if LLM fails
        debug(f"LLM error: {str(e)}", "ORCHESTRATOR")
        import random
        valid_speakers = ["abhishek", "abhijit", "santhi", "govind"]
        selected_speaker = random.choice(valid_speakers)
        debug(f"LLM error, random selection: {selected_speaker}", "ORCHESTRATOR")

    debug(f"Final selection: {selected_speaker} (volley {volley_left} -> {volley_left - 1})", "ORCHESTRATOR")

    # Return only the updates (LangGraph will merge with existing state)
    return {
        "next_speaker": selected_speaker,
        "volley_msg_left": volley_left - 1
    }
