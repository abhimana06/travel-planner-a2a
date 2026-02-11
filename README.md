# Singapore Travel Planning Committee

A LangGraph-based agentic workflow for planning trips to Singapore with a committee of specialized agents.

## Set up

### Option 1: Using venv (Recommended)

```sh
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
# or: venv\Scripts\activate  # On Windows

# Install dependencies
pip install -e .
```

### Option 2: Using uv

```sh
uv sync
```

**Note:** If using uv with an existing venv, deactivate it first or use `uv sync --active`

### Configure Environment Variables

Create a `.env` file in the project root:

```sh
OPENAI_API_KEY=your_openai_api_key_here
```

Get your OpenAI API key from: https://platform.openai.com/api-keys

## Running the Application

```sh
python main.py
```

## How to Use

### 1. Start the Application
When you run `python main.py`, you'll see:
```
=== SINGAPORE TRAVEL PLANNING COMMITTEE ===
Plan your dream Singapore trip! Type 'exit' when done.

Setting: A travel planning committee meeting...
The team is ready - Abhishek (travel enthusiast),
Abhijit (social media influencer), Santhi (budget planner),
and Govind (itinerary specialist).

You:
```

### 2. Provide Your Travel Requirements
Type your travel preferences, budget, and requirements. For example:
```
You: I want a 3-day Singapore itinerary for $500 budget
```

### 3. Committee Discussion (5 Volleys)
The committee will automatically discuss and plan:
- **Abhishek** suggests exciting destinations
- **Abhijit** recommends Instagram-worthy spots
- **Santhi** analyzes budget and costs
- **Govind** creates detailed itinerary

The discussion continues for 5 exchanges, then returns to you for more input.

### 4. Continue Planning or Get Summary
After the 5 volleys:
- Provide more requirements or ask questions
- Or type `exit` to end and get summary

### 5. Exit and Get Summary
Type:
```
You: exit
```

The system will generate a comprehensive summary including:
- **Destinations & Attractions** - All proposed locations
- **Budget Analysis** - Cost breakdown and recommendations
- **Itinerary Planning** - Day-by-day schedule
- **Social Media Spots** - Instagram-worthy locations
- **Committee Insights** - Contributions from each member
- **Action Items** - Next steps for your trip

### Example Session

```
You: Plan a 2-day trip with $800 budget, I love food and culture

[Committee discusses for 5 volleys]

You: What about family-friendly activities?

[Committee discusses for 5 more volleys]

You: exit

=== TRAVEL PLANNING SESSION ENDING ===

=== TRAVEL PLANNING COMMITTEE SUMMARY ===
[Detailed summary of all discussions and recommendations]

Thank you! Happy travels and see you next time!
```

## Project Overview

This project implements a multi-agent system for travel planning with:
- **Abhishek** - Travel enthusiast who initiates trip ideas
- **Abhijit** - Social media influencer suggesting trending destinations
- **Santhi** - Budget planner ensuring financial feasibility
- **Govind** - Itinerary specialist creating detailed plans

## Starter steps

1. Sketch Graph
1. Go through dependencies
1. Define State
1. Define Tools (travel, weather, news)
1. Define Agents (orchestrator, participants, summarizer)
1. Define Nodes
1. Define Graph (main.py)
