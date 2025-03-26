from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import httpx
import json
import os
from bs4 import BeautifulSoup
import boto3
from agentselector import BedrockAgentSelector

load_dotenv()

mcp = FastMCP("aws-mcp")

@mcp.tool()  
async def agent_registry(query: str):
    """Query the Agent registry for information related to Agentic memory and Agents roles in Software Engineering
    
    Args:
        query: The query string to search for
    """
    agent_selector = BedrockAgentSelector()
    best_agent = agent_selector.select_agent(query)
    response_text = agent_selector.invoke_agent(best_agent, query)

    return response_text['response']


if __name__ == "__main__":
    mcp.run(transport="stdio")

@mcp.tool()
async def kb_registry(query: str):
    """Query the Knowledgebase registry for information related to Agentic memory and Agents roles in Software Engineering
    
    Args:
        query: The query string to search for
    """
    agent_selector = BedrockAgentSelector()
    best_agent = agent_selector.select_agent(query)
    response_text = agent_selector.invoke_agent(best_agent, query)

    return response_text['response']




if __name__ == "__main__":
    mcp.run(transport="stdio")

