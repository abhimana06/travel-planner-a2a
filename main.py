from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END

from state import State
from agents import orchestrator
from nodes import (
    human_node,
    check_exit_condition,
    orchestrator_routing,
    participant_node,
    summarizer_node
)


load_dotenv(override=True)  # Override, so it would use your local .env file




def build_graph():
    """
    Build the LangGraph workflow.
    """

    builder = StateGraph(State)

    # Add nodes
    builder.add_node("human", human_node)
    builder.add_node("orchestrator", orchestrator)  # Use orchestrator directly
    builder.add_node("participant", participant_node)
    builder.add_node("summarizer", summarizer_node)

    # Edges
    builder.add_edge(START, "human")

    builder.add_conditional_edges(
        "human",
        check_exit_condition,
        {
            "summarizer": "summarizer",
            "orchestrator": "orchestrator"
        }
    )

    builder.add_conditional_edges(
        "orchestrator",
        orchestrator_routing,
        {
            "participant": "participant",
            "human": "human"
        }
    )

    builder.add_edge("participant", "orchestrator")

    builder.add_edge("summarizer", END)

    return builder.compile()


def main():
    print("=== SINGAPORE TRAVEL PLANNING COMMITTEE ===")
    print("Plan your dream Singapore trip! Type 'exit' when done.\n")
    print("Setting: A travel planning committee meeting...")
    print("The team is ready - Abhishek (travel enthusiast),")
    print("Abhijit (social media influencer), Santhi (budget planner),")
    print("and Govind (itinerary specialist).\n")

    graph = build_graph()

    print(graph.get_graph().draw_ascii())

    initial_state = State(
        messages=[],
        volley_msg_left=0,
        next_speaker=None
    )

    try:
        graph.invoke(initial_state)
    except KeyboardInterrupt:
        print("\n\nConversation interrupted. Goodbye!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Ending conversation...")


if __name__ == "__main__":
    main()
