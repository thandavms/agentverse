# Bedrock Agent Assistant

A Python-based tool for intelligent agent selection and interaction using Amazon Bedrock Agents. This project provides functionality to semantically match user queries with the most appropriate Bedrock agent and handle agent interactions.

## Features

- Semantic matching of user queries to appropriate Bedrock agents
- Automatic agent selection based on similarity scoring
- Agent response streaming and processing
- Support for multiple agents with different capabilities
- Caching of agent information for improved performance

## Prerequisites

- Python 3.7+
- AWS credentials configured
- Access to Amazon Bedrock service
- Required Python packages:
  - boto3
  - numpy

## Installation

1. Clone the repository
2. Install the required dependencies:
```bash
pip install boto3 numpy
```

## Usage

```python
from agentselector import BedrockAgentSelector

# Initialize the selector
agent_selector = BedrockAgentSelector(region="us-west-2")

# Get a list of all available agents
agents = agent_selector.get_all_agents()

# Select and invoke an agent with a query
best_agent = agent_selector.select_agent("What's the weather like today?")
response = agent_selector.invoke_agent(best_agent, "What's the weather like today?")
```
## Key Components

BedrockAgentSelector: Main class that handles agent selection and interaction

get_all_agents(): Retrieves and caches available Bedrock agents

select_agent(): Selects the most appropriate agent for a given query

invoke_agent(): Invokes the selected agent and processes its response