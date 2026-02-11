from tools import singapore_travel, singapore_weather, singapore_news
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from utils import debug
import re
import httpx


# Persona configurations
PERSONAS = {
    "abhishek": {
        "name": "abhishek",
        "age": 33,
        "backstory": "Adventurous traveler who loves exploring new destinations, dreams of visiting exotic locations",
        "personality": "Enthusiastic, spontaneous, passionate about travel experiences, eager to plan trips",
        "speech_style": "Excited and energetic, uses phrases like 'Let's go!', 'This would be amazing!'",
        "tools": ["travel", "weather"]
    },
    "abhijit": {
        "name": "abhijit",
        "age": 21,
        "backstory": "Social media influencer specializing in travel content, knows trending destinations and Instagram-worthy spots",
        "personality": "Trendy, social media savvy, enthusiastic about viral destinations, loves aesthetic experiences",
        "speech_style": "Modern and upbeat, uses 'OMG', 'Insta-worthy', 'This will get so many likes!'",
        "tools": ["travel", "news"]
    },
    "santhi": {
        "name": "santhi",
        "age": 45,
        "backstory": "Former financial analyst, now specializes in travel budget planning and cost optimization",
        "personality": "Analytical, practical, cost-conscious, data-driven, ensures trips stay within budget",
        "speech_style": "Professional and precise, makes financial references, talks about ROI and value for money",
        "tools": ["travel"]
    },
    "govind": {
        "name": "govind",
        "age": 72,
        "backstory": "Experienced itinerary specialist with 40+ years of travel planning, knows hidden gems worldwide",
        "personality": "Methodical, knowledgeable, detail-oriented, patient, ensures seamless travel experiences",
        "speech_style": "Thoughtful and measured, provides detailed recommendations, asks clarifying questions",
        "tools": ["travel", "weather", "news"]  # Govind has ALL tools
    }
}


def execute_tool(tool_name):
    """
    Execute a specific tool and return its output.
    Returns Tool output as string
    """
    tool_name = tool_name.lower().strip()

    if tool_name == "travel":
        return singapore_travel()
    elif tool_name == "weather":
        return singapore_weather()
    elif tool_name == "news":
        return singapore_news()
    else:
        return f"Unknown tool: {tool_name}"


def participant(persona_id, state) -> dict:
    """
    Generate speech for a persona using ReAct workflow with real tool calling.

    Args:
        persona_id: One of "abhishek", "abhijit", "santhi", "govind"
        state: Current conversation state

    Returns:
        Dict with message updates for state
    """
    if persona_id not in PERSONAS:
        return {"messages": [{"role": "assistant", "content": f"Unknown persona: {persona_id}"}]}

    persona = PERSONAS[persona_id]
    debug(f"\n=== {persona['name']} is thinking... ===")

    # Get recent conversation for context
    messages = state.get("messages", [])
    conversation_text = ""
    for msg in messages:
        conversation_text += f"{msg.get('content', '')}\n"

    # Tool descriptions mapping
    tool_descriptions = {
        "travel": "Returns popular Singapore travel destinations and attractions",
        "weather": "Returns current weather in Singapore",
        "news": "Returns latest Singapore travel and tourism news"
    }

    # Build available actions list based on persona's tools
    available_actions = ""
    for tool in persona['tools']:
        available_actions += f"\n\n{tool}:\n{tool_descriptions[tool]}"

    # System prompt for ReAct
    system_prompt = f"""You are {persona['name']}, {persona['age']} years old.
Background: {persona['backstory']}
Personality: {persona['personality']}
Speech style: {persona['speech_style']}

You are part of a travel planning committee organizing a trip to Singapore based on user preferences and budget.

You run in a loop of Thought, Action, Observation.
At the end of the loop you output a Message.

Use Thought to describe your thoughts about the conversation.
Use Action to run one of the actions available to you.
Observation will be the result of running those actions.

Possible actions are:

{available_actions}

You only have access to the tools/actions listed above. Do not call tools that you do not have access to.

------

Example session:

Thought: I should check what travel destinations are available to help plan this trip
Action: travel

You will be called again with:
Observation: [Travel information will be returned after you call the tool]

You must never try to guess the time or weather or news. Rely on the Observation that you will be called later on for the answers. You MUST NOT answer with those.

You then continue thinking or output:
Message: [Your response in character]

IMPORTANT:
- You can use multiple actions by continuing the loop
- You must not be providing Observation in your response. Observation is a result from tool, not for you to respond.
- Once you have enough information, output Message: followed by your response
- Keep your Message concise (2-3 sentences) and in character
- Focus on travel planning aspects relevant to your role (destination ideas, budget, itinerary, or social media appeal)
"""

    # Internal loop for ReAct
    max_iterations = 5  # Prevent infinite loops
    internal_context = f"Recent travel planning discussion:\n{conversation_text}\n\nContinue contributing to the travel planning as {persona['name']}.\n"

    for iteration in range(max_iterations):
        user_prompt = internal_context
        debug(f"Iteration {iteration + 1}/{max_iterations}")

        try:
            http_client = httpx.Client(verify=False)
            llm = ChatOpenAI(model="gpt-4o-mini", temperature=1, http_client=http_client)
            response = llm.invoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=user_prompt)
            ])
            content = response.content.strip()
            debug(f"LLM Response:\n{content}\n")

            # Check if the response contains Message:
            if "Message:" in content:
                # Extract the message
                message_match = re.search(r'Message:\s*(.*)', content, re.DOTALL)
                if message_match:
                    final_message = message_match.group(1).strip()
                    debug(f"Final Message: {final_message}")
                    debug(f"=== End of {persona['name']}'s thought process ===\n")

                    # Return the message to state
                    return {
                        "messages": [{
                            "role": "assistant",
                            "name": persona['name'],
                            "content": f"\n{persona['name']}: {final_message}\n\n"
                        }]
                    }

            # Check if the response contains Action:
            if "Action:" in content:
                # Extract the action
                action_match = re.search(r'Action:\s*(\w+)', content)
                if action_match:
                    tool_name = action_match.group(1)
                    debug(f"Executing tool: {tool_name}")

                    # Execute the tool
                    observation = execute_tool(tool_name)
                    debug(f"Observation: {observation}")
                    debug("")  # Empty line for readability

                    # Add observation to internal context
                    internal_context += f"\n{content}\n\nObservation: {observation}\n"
                    continue

            # If we get here without action or message, add to context and continue
            internal_context += f"\n{content}\n"

        except Exception as e:
            # Fallback response if LLM fails
            debug(f"Error in participant node for {persona['name']}: {str(e)}")
            return {
                "messages": [{
                    "role": "assistant",
                    "name": persona['name'],
                    "content": f"{persona['name']}: Sorry ah, my mind a bit blur now..."
                }]
            }

    # If we exhausted iterations without getting a Message, provide default
    return {
        "messages": [{
            "role": "assistant",
            "name": persona['name'],
            "content": f"{persona['name']}: Well, that's interesting lah..."
        }]
    }
