import streamlit as st
import boto3
import json
import uuid
from agentselector import BedrockAgentSelector

# Set up the page configuration
st.set_page_config(page_title="Amazon Bedrock Agent Assistant", page_icon="🤖")

# Initialize session state variables if they don't exist
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

def initialize_bedrock_client(region):
    """Initialize and return the Amazon Bedrock client"""
    try:
        # Initialize the Bedrock client
        bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name = region)
        return bedrock_agent_runtime
    except Exception as e:
        st.error(f"Error initializing Bedrock client: {str(e)}")
        return None

def list_available_agents(client, region):
    """Get a list of available Bedrock agents"""
    try:
        # Use the Bedrock client to list agents
        # Note: This is a simplified approach. In a real application, 
        # you might use the bedrock-agent service to list agents
        bedrock_agent = boto3.client('bedrock-agent', region_name = region)
        response = bedrock_agent.list_agents()
        return response.get('agentSummaries', [])
    except Exception as e:
        st.error(f"Error listing agents: {str(e)}")
        return []


# Main app UI
st.title("🤖 Amazon Bedrock Agent Assistant")
st.markdown("Ask a question and I'll find the right agent to help you!")

# Initialize the Bedrock client
bedrock_client = initialize_bedrock_client("us-west-2")

# User input
user_query = st.text_input("Your question:", key="user_input")

# Process the query when submitted
if user_query:
    with st.spinner("Processing your question..."):
        # Add user query to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_query})
        
        # List available agents
        agents = list_available_agents(bedrock_client, "us-west-2")
        
        if not agents:
            response_text = "No agents available in the registry. Please check your AWS configuration."
        else:
            st.info(f"Finding the suitable agent from availble agents: {len(agents)}")
            agent_selector = BedrockAgentSelector()
            best_agent = agent_selector.select_agent(user_query)
            
            if not best_agent:
                response_text = "Couldn't find a suitable agent for your query."
            else:
                # Query the selected agent
                agent_id = best_agent.get('agentId')
                agent_name = best_agent.get('name')
                
                print(best_agent)
                st.info(f"Using agent: {agent_name}")

                response_text = agent_selector.invoke_agent(best_agent, user_query)
        
        # Add response to chat history
        st.session_state.chat_history.append({"role": "assistant", "content": response_text['response']})

# Display chat history
st.markdown("### Conversation")
for message in st.session_state.chat_history:
    role = message["role"]
    content = message["content"]
    
    if role == "user":
        st.markdown(f"**You:** {content}")
    else:
        st.markdown(f"**Assistant:** {content}")
    
    st.markdown("---")

# Add some instructions at the bottom
st.markdown("""
### How to use
1. Type your question in the text box
2. The app will search through available Amazon Bedrock agents
3. It will select the most relevant agent to answer your question
4. The response will appear in the conversation area
""")