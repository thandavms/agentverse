import streamlit as st
import boto3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import time
from datetime import datetime, timedelta
import os
from botocore.exceptions import ClientError
import uuid
from dotenv import load_dotenv

# Set page configuration
st.set_page_config(
    page_title="Agent Registry",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional appearance
st.markdown("""
<style>
    /* Typography */
    body {
        font-family: 'Inter', 'Segoe UI', Tahoma, sans-serif;
        color: #1A1A1A;
    }
    
    h1, h2, h3, h4, h5, h6 {
        font-weight: 600;
        color: #0F1A2A;
    }
    
    /* Header Styles */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #232F3E, #FF9900);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1.5rem;
        text-align: center;
        padding: 0.5rem 0;
    }
    
    .section-header {
        font-size: 1.5rem;
        font-weight: 600;
        color: #232F3E;
        margin: 1.2rem 0 0.8rem 0;
        padding-bottom: 0.3rem;
        border-bottom: 2px solid #FF9900;
    }
    
    /* Card Components */
    .dashboard-card {
        background: white;
        border-radius: 8px;
        padding: 1.5rem;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 1.5rem;
        border-top: 4px solid #FF9900;
    }
    
    .metric-card {
        background: linear-gradient(to bottom right, #FFFFFF, #F9FAFB);
        border-radius: 8px;
        padding: 1.2rem;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.08);
        margin-bottom: 1rem;
        transition: transform 0.2s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #232F3E;
    }
    
    .metric-label {
        font-size: 1rem;
        color: #5F6B7A;
        margin-bottom: 0;
    }
    
    /* Button Styling */
    .stButton > button {
        background-color: #FF9900;
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #E88A00;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        transform: translateY(-1px);
    }
    
    /* Badge/Tag Styling */
    .badge {
        display: inline-block;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.8rem;
        font-weight: 500;
        margin-right: 0.5rem;
    }
    
    .badge-blue {
        background-color: #E1F5FE;
        color: #0277BD;
    }
    
    .badge-green {
        background-color: #E8F5E9;
        color: #2E7D32;
    }
    
    .badge-amber {
        background-color: #FFF8E1;
        color: #FF8F00;
    }
    
    /* Code Display */
    .code-block {
        background-color: #F5F7F9;
        border-radius: 5px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        overflow-x: auto;
        border-left: 3px solid #FF9900;
    }
    
    /* Layout helpers */
    .flex-container {
        display: flex;
        flex-wrap: wrap;
        gap: 1rem;
    }
    
    /* Status indicators */
    .status-indicator {
        width: 12px;
        height: 12px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
    
    .status-active {
        background-color: #4CAF50;
    }
    
    .status-inactive {
        background-color: #9E9E9E;
    }
    
    .status-error {
        background-color: #F44336;
    }
    
    /* Improve default Streamlit component styling */
    .stSelectbox label, .stSlider label {
        font-weight: 500;
        color: #232F3E;
    }
    
    /* Tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: #F5F7F9;
        border-radius: 4px 4px 0 0;
        padding: 10px 16px;
        border: none;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #FF9900 !important;
        color: white !important;
    }
    
    /* Sidebar enhancements */
    .css-1d391kg {
        background-color: #F5F7F9;
    }
    
    /* Responsive adjustments */
    @media (max-width: 768px) {
        .main-header {
            font-size: 2rem;
        }
        .section-header {
            font-size: 1.3rem;
        }
    }
    
    /* Alert boxes */
    .info-box {
        background-color: #E3F2FD;
        border-left: 4px solid #2196F3;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .warning-box {
        background-color: #FFF3E0;
        border-left: 4px solid #FF9800;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .error-box {
        background-color: #FFEBEE;
        border-left: 4px solid #F44336;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
    
    .success-box {
        background-color: #E8F5E9;
        border-left: 4px solid #4CAF50;
        padding: 1rem;
        border-radius: 4px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Utility functions
def get_aws_credentials():
    """
    Get AWS credentials securely. 
    In production, use environment variables or AWS IAM roles instead of hardcoding.
    """
    # Use environment variables for production
    load_dotenv()
    access_key = os.environ.get('ACCESS_KEY')
    secret_key = os.environ.get('SECRET_KEY')
    region = os.environ.get('AWS_REGION', 'us-west-2')  # Default to us-west-2 if not set
    
    # If environment variables aren't set, use secure inputs
    # (For development only - not recommended for production)
    if not (access_key and secret_key):
        st.sidebar.markdown("### AWS Credentials")
        st.sidebar.warning("⚠️ For production, use environment variables or IAM roles")
        access_key = st.sidebar.text_input("AWS Access Key ID:", type="password")
        secret_key = st.sidebar.text_input("AWS Secret Access Key:", type="password")
    
    return access_key, secret_key, region

@st.cache_resource
def initialize_clients(access_key, secret_key, region):
    """Initialize and cache AWS client connections."""
    if not access_key or not secret_key:
        return None, None, None, None
    
    try:
        session = boto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )
        
        bedrock_agent = session.client('bedrock-agent', region_name=region)
        bedrock_agent_runtime = session.client('bedrock-agent-runtime', region_name=region)
        bedrock = session.client('bedrock', region_name=region)
        cloudwatch = session.client('cloudwatch', region_name=region)
        
        return bedrock_agent, bedrock_agent_runtime, bedrock, cloudwatch
    except Exception as e:
        st.error(f"Failed to initialize AWS clients: {str(e)}")
        return None, None, None, None

def get_all_agents(bedrock_agent):
    """Get all Bedrock agents with pagination and caching."""
    if not bedrock_agent:
        return []
        
    try:
        agents = []
        paginator = bedrock_agent.get_paginator('list_agents')
        
        with st.spinner("Loading agents..."):
            for page in paginator.paginate():
                agents.extend(page.get('agentSummaries', []))
        
        return agents
    except Exception as e:
        st.error(f"Error fetching agents: {str(e)}")
        return []

def get_agent_details(bedrock_agent, agent_id):
    """Get detailed information about a specific agent."""
    if not bedrock_agent or not agent_id:
        return None
        
    try:
        response = bedrock_agent.get_agent(agentId=agent_id)
        return response.get('agent')
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == 'ResourceNotFoundException':
            st.error(f"Agent {agent_id} not found.")
        else:
            st.error(f"AWS Error: {error_code} - {e.response['Error']['Message']}")
        return None
    except Exception as e:
        st.error(f"Error fetching agent details: {str(e)}")
        return None

def get_agent_action_groups(bedrock_agent, agent_id):
    """Get action groups associated with an agent."""
    if not bedrock_agent or not agent_id:
        return []
        
    try:
        action_groups = []
        paginator = bedrock_agent.get_paginator('list_agent_action_groups')
        for page in paginator.paginate(agentId=agent_id, agentVersion='DRAFT'):
            action_groups.extend(page.get('actionGroupSummaries', []))
        return action_groups
    except Exception as e:
        st.error(f"Error fetching action groups: {str(e)}")
        return []

def get_agent_knowledge_bases(bedrock_agent, agent_id):
    """Get knowledge bases associated with an agent."""
    if not bedrock_agent or not agent_id:
        return []
        
    try:
        knowledge_bases = []
        paginator = bedrock_agent.get_paginator('list_agent_knowledge_bases')
        for page in paginator.paginate(agentId=agent_id, agentVersion='DRAFT'):
            knowledge_bases.extend(page.get('agentKnowledgeBaseSummaries', []))
        return knowledge_bases
    except Exception as e:
        st.error(f"Error fetching knowledge bases: {str(e)}")
        return []

def get_knowledge_base_details(bedrock_agent, kb_id):
    """Get details about a specific knowledge base."""
    if not bedrock_agent or not kb_id:
        return None
        
    try:
        response = bedrock_agent.get_knowledge_base(knowledgeBaseId=kb_id)
        return response
    except Exception as e:
        st.error(f"Error fetching knowledge base details: {str(e)}")
        return None

def get_agent_aliases(bedrock_agent, agent_id):
    """Get all aliases associated with an agent."""
    if not bedrock_agent or not agent_id:
        return []
        
    try:
        aliases = []
        paginator = bedrock_agent.get_paginator('list_agent_aliases')
        for page in paginator.paginate(agentId=agent_id):
            aliases.extend(page.get('agentAliasSummaries', []))
        return aliases
    except Exception as e:
        st.error(f"Error fetching agent aliases: {str(e)}")
        return []

def get_agent_metrics(cloudwatch, agent_id, days=7):
    """Get CloudWatch metrics for an agent with improved handling."""
    if not cloudwatch or not agent_id:
        return {}
        
    try:
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        metrics = [
            {
                'name': 'Invocations',
                'namespace': 'AWS/Bedrock',
                'metric': 'InvocationCount',
                'stat': 'Sum',
                'dimensions': [{'Name': 'AgentId', 'Value': agent_id}],
                'color': '#4CAF50'
            },
            {
                'name': 'Latency (ms)',
                'namespace': 'AWS/Bedrock',
                'metric': 'Latency',
                'stat': 'Average',
                'dimensions': [{'Name': 'AgentId', 'Value': agent_id}],
                'color': '#2196F3'
            },
            {
                'name': 'Errors',
                'namespace': 'AWS/Bedrock',
                'metric': 'ErrorCount',
                'stat': 'Sum',
                'dimensions': [{'Name': 'AgentId', 'Value': agent_id}],
                'color': '#F44336'
            }
        ]
        
        results = {}
        for metric in metrics:
            try:
                response = cloudwatch.get_metric_statistics(
                    Namespace=metric['namespace'],
                    MetricName=metric['metric'],
                    Dimensions=metric['dimensions'],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,  # Daily data points
                    Statistics=[metric['stat']]
                )
                
                datapoints = sorted(response.get('Datapoints', []), key=lambda x: x['Timestamp'])
                
                if datapoints:
                    timestamps = [dp['Timestamp'] for dp in datapoints]
                    values = [dp[metric['stat']] for dp in datapoints]
                    
                    results[metric['name']] = {
                        'timestamps': timestamps,
                        'values': values,
                        'color': metric['color']
                    }
                else:
                    results[metric['name']] = {
                        'timestamps': [],
                        'values': [],
                        'color': metric['color']
                    }
            except Exception as e:
                st.warning(f"Failed to fetch {metric['name']} metric: {str(e)}")
                continue
        
        return results
    except Exception as e:
        st.warning(f"Could not fetch metrics: {str(e)}")
        return {}

def invoke_agent(bedrock_agent_runtime, agent_id, agent_alias_id, prompt):
    """Invoke an agent with a prompt and proper error handling."""
    if not all([bedrock_agent_runtime, agent_id, agent_alias_id, prompt]):
        st.error("Missing required parameters to invoke agent")
        return None
        
    try:
        response = bedrock_agent_runtime.invoke_agent(
            agentId=agent_id,
            agentAliasId=agent_alias_id,
            sessionId=f"streamlit-{uuid.uuid4()}",
            inputText=prompt
        )

        # Process streaming response
        event_stream = response.get('completion')
        complete_response = ""
        trace_info = {}
        
        with st.spinner("Agent is responding..."):
            try:
                for event in event_stream:
                    if 'chunk' in event:
                        chunk = event['chunk']['bytes'].decode('utf8')
                        complete_response += chunk
                        
                    elif 'trace' in event:
                        trace_info = event['trace']
            except Exception as e:
                st.error(f"Error processing agent response: {str(e)}")
                return None
        
        return {
            'completion': complete_response,
            'trace': trace_info
        }
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        st.error(f"AWS Error ({error_code}): {error_message}")
        return None
    except Exception as e:
        st.error(f"Error invoking agent: {str(e)}")
        return None

def format_timestamp(ts):
    """Format timestamp in a human-readable way."""
    if not ts:
        return "N/A"
    
    if isinstance(ts, datetime):
        return ts.strftime('%Y-%m-%d %H:%M:%S UTC')
    return str(ts)

def get_agent_subagents(bedrock_agent, agent_id):
    """Get subagents associated with an agent."""
    if not bedrock_agent or not agent_id:
        return []
        
    try:
        subagents = []
        response = bedrock_agent.list_agent_collaborators(
            agentId=agent_id,
            agentVersion="DRAFT"
        )

        for collaborator in response["agentCollaboratorSummaries"]:
            subagents.append({
                "name": collaborator['collaboratorName'],
                "id": collaborator['collaboratorId'],
            })

        return subagents
    except Exception as e:
        st.error(f"Error fetching subagents: {str(e)}")
        return []

# App state initialization
if 'selected_agent' not in st.session_state:
    st.session_state.selected_agent = None

if 'test_conversation' not in st.session_state:
    st.session_state.test_conversation = []

# Main application function
def main():
    # Display header
    st.markdown("<h1 class='main-header'>🤖 Agent Registry</h1>", unsafe_allow_html=True)
    
    # Get AWS credentials
    access_key, secret_key, region = get_aws_credentials()
    
    if not access_key or not secret_key:
        st.markdown(
            """
            <div class="warning-box">
                <h3>AWS Credentials Required</h3>
                <p>Please provide your AWS credentials to access your Bedrock agents. 
                For production use, set these as environment variables or use IAM roles.</p>
            </div>
            """, 
            unsafe_allow_html=True
        )
        return
    
    # Initialize AWS clients
    bedrock_agent, bedrock_agent_runtime, bedrock, cloudwatch = initialize_clients(access_key, secret_key, region)
    
    if not bedrock_agent:
        return
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown("<h3 class='sidebar-header'>Agent Navigator</h3>", unsafe_allow_html=True)
        
        # Region selector
        regions = ['us-west-2', 'us-east-1', 'eu-central-1', 'eu-west-1']
        selected_region = st.selectbox("AWS Region:", regions, index=0)
        
        # Refresh button
        if st.button("🔄 Refresh Agents"):
            # Clear cache to get fresh data
            print(selected_region)
            st.session_state.agents = ''
            st.session_state.selected_agent =''
            bedrock_agent, bedrock_agent_runtime, bedrock, cloudwatch = initialize_clients(access_key, secret_key, selected_region)
            st.session_state.agents = get_all_agents(bedrock_agent)
            st.success("✅ Agent list refreshed!")
        
        # Load or refresh agent list
        if 'agents' not in st.session_state or not st.session_state.agents:
            print("was i here with")
            st.session_state.agents = get_all_agents(bedrock_agent)
        
        # Display agent count
        if len(st.session_state.agents) != 0:
            st.markdown(f"**Found {len(st.session_state.agents)} agents**")
            
            # Agent selection
            agent_options = {agent['agentName']: agent['agentId'] for agent in st.session_state.agents}
            selected_agent_name = st.selectbox(
                "Select an agent:",
                options=list(agent_options.keys()),
                index=0 if st.session_state.selected_agent is None else 
                      next((i for i, id in enumerate(agent_options.values()) 
                          if id == st.session_state.selected_agent), 0)
            )
            
            st.session_state.selected_agent = agent_options[selected_agent_name]
        else:
            st.warning("No agents found in your account.")
        
        # Metrics time range
        st.markdown("---")
        st.markdown("### Metrics Settings")
        metrics_days = st.slider("Historical data (days):", 1, 30, 7)
    
    # Main content area
    if st.session_state.selected_agent:
        agent_id = st.session_state.selected_agent
        
        # Fetch all necessary data
        with st.spinner("Loading agent data..."):
            agent_details = get_agent_details(bedrock_agent, agent_id)
            action_groups = get_agent_action_groups(bedrock_agent, agent_id)
            knowledge_bases = get_agent_knowledge_bases(bedrock_agent, agent_id)
            agent_aliases = get_agent_aliases(bedrock_agent, agent_id)
            metrics = get_agent_metrics(cloudwatch, agent_id, metrics_days)
        
        if agent_details:
            # Agent header section
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.markdown(f"<h2 class='section-header'>{agent_details['agentName']}</h2>", unsafe_allow_html=True)
                
                # Status indicator
                status = agent_details.get('agentStatus', 'UNKNOWN')
                status_color = {
                    'CREATING': '🟡',
                    'ACTIVE': '🟢',
                    'FAILED': '🔴',
                    'DELETING': '⚪',
                    'UPDATING': '🔵',
                    'UNKNOWN': '⚪'
                }.get(status, '⚪')
                
                st.markdown(f"{status_color} **Status:** {status}")
                
                if agent_details.get('description'):
                    st.markdown(f"**Description:** {agent_details['description']}")
                
                # Key details in columns for better organization
                col_id, col_model, col_created = st.columns(3)
                with col_id:
                    st.markdown("**ID**")
                    st.code(agent_id, language=None)
                
                with col_model:
                    st.markdown("**Foundation Model**")
                    st.markdown(f"`{agent_details.get('foundationModel', 'Not specified')}`")
                
                with col_created:
                    st.markdown("**Created**")
                    st.markdown(format_timestamp(agent_details.get('createdAt')))
            
            with col2:
                # Key metrics
                st.markdown("### 📊 Quick Stats")
                
                metric1, metric2, metric3 = st.columns(3)
                with metric1:
                    st.metric("Action Groups", len(action_groups))
                
                with metric2:
                    st.metric("Knowledge Bases", len(knowledge_bases))

                with metric3:
                    subagents = get_agent_subagents(bedrock_agent, agent_id)
                    st.metric("Sub Agents", len(subagents))
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            # Tabs for detailed information
            tabs = st.tabs(["📋 Overview", "🛠️ Action Groups", "📚 Knowledge Bases", "🔬 Test Agent", "📈 Metrics"])
            
            with tabs[0]:  # Overview tab
                st.markdown("### Agent Configuration")
                
                # Agent instructions
                if 'instruction' in agent_details and agent_details['instruction']:
                    with st.expander("Agent Instructions", expanded=True):
                        st.markdown(agent_details['instruction'])
                
                # Agent capabilities visualization
                st.markdown("### Agent Capabilities")
                
                cap1, cap2, cap3 = st.columns(3)
                
                with cap1:
                    # Get subagents for this agent
                    
                    subagents = get_agent_subagents(bedrock_agent, agent_id)
                    subagent_badge = "badge-green" if subagents else "badge-amber"
                    subagent_status = "Configured" if subagents else "Not Configured"
                    
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4>Subagents</h4>
                            <p>{len(subagents)} Subagents</p>
                            <div class="badge {subagent_badge}">{subagent_status}</div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                
                with cap2:
                    action_group_badge = "badge-green" if action_groups else "badge-amber"
                    action_status = "Configured" if action_groups else "Not Configured"
                    
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4>Tool Integration</h4>
                            <p>{len(action_groups)} Action Groups</p>
                            <div class="badge {action_group_badge}">{action_status}</div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                
                with cap3:
                    kb_badge = "badge-green" if knowledge_bases else "badge-amber"
                    kb_status = "Configured" if knowledge_bases else "Not Configured"
                    
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4>Knowledge Base Access</h4>
                            <p>{len(knowledge_bases)} Knowledge Bases</p>
                            <div class="badge {kb_badge}">{kb_status}</div>
                        </div>
                        """, 
                        unsafe_allow_html=True
                    )
                
                # Raw configuration (for advanced users)
                with st.expander("Advanced: Raw Configuration"):
                    # Filter out sensitive data
                    safe_config = {k: v for k, v in agent_details.items() 
                                 if k not in ['responseMetadata', 'securityConfig']}
                    st.json(safe_config)
            
            with tabs[1]:  # Action Groups tab
                st.markdown("### Action Groups")
                
                if not action_groups:
                    st.info("This agent has no configured action groups.")
                else:
                    for idx, action_group in enumerate(action_groups):
                        with st.expander(f"{action_group['actionGroupName']}"):
                            st.markdown(f"**ID:** `{action_group['actionGroupId']}`")
                            
                            if action_group.get('description'):
                                st.markdown(f"**Description:** {action_group['description']}")
                            
                            st.markdown(f"**Created:** {format_timestamp(action_group.get('createdAt'))}")
                            
                            # Try to get action group details and schema
                            try:
                                action_group_details = bedrock_agent.get_agent_action_group(
                                    agentId=agent_id,
                                    agentVersion='DRAFT',
                                    actionGroupId=action_group['actionGroupId']
                                )
                                
                                if 'apiSchema' in action_group_details:
                                    st.markdown("#### API Schema")
                                    schema = json.dumps(json.loads(action_group_details['apiSchema']), indent=2)
                                    st.markdown(f"<pre class='code-block'>{schema}</pre>", unsafe_allow_html=True)
                            except Exception as e:
                                st.warning(f"Could not fetch schema: {str(e)}")
            
            with tabs[2]:  # Knowledge Bases tab
                st.markdown("### Knowledge Bases")
                
                if not knowledge_bases:
                    st.info("This agent has no associated knowledge bases.")
                else:
                    for kb in knowledge_bases:
                        with st.expander(f"{kb.get('knowledgeBaseName', kb['knowledgeBaseId'])}"):
                            kb_id = kb['knowledgeBaseId']
                            
                            # Get knowledge base details
                            kb_details = get_knowledge_base_details(bedrock_agent, kb_id)
                            
                            if kb_details:
                                st.markdown(f"**ID:** `{kb_id}`")
                                
                                if kb_details.get('description'):
                                    st.markdown(f"**Description:** {kb_details['description']}")
                                
                                st.markdown(f"**Created:** {format_timestamp(kb_details.get('createdAt'))}")
                                
                                # Storage configuration
                                storage_type = kb_details.get('storageConfiguration', {}).get('type', 'Unknown')
                                st.markdown(f"**Storage Type:** {storage_type}")
                                
                                # Data sources
                                try:
                                    data_sources = bedrock_agent.list_knowledge_base_data_sources(
                                        knowledgeBaseId=kb_id
                                    )
                                    
                                    if data_sources.get('dataSourceSummaries'):
                                        st.markdown("#### Data Sources")
                                        
                                        for ds in data_sources['dataSourceSummaries']:
                                            st.markdown(
                                                f"""
                                                <div class='metric-card'>
                                                    <h5>{ds.get('name', 'Unnamed Source')}</h5>
                                                    <p><code>{ds.get('dataSourceId')}</code></p>
                                                    <p>Status: {ds.get('status', 'Unknown')}</p>
                                                </div>
                                                """,
                                                unsafe_allow_html=True
                                            )
                                except Exception as e:
                                    st.warning(f"Could not fetch data sources: {str(e)}")
            
            with tabs[3]:  # Test Agent tab
                st.markdown("### Test Your Agent")
                
                if not agent_aliases:
                    st.error("This agent has no aliases. An alias is required to invoke the agent.")
                else:
                    # Select an alias
                    alias_options = {alias['agentAliasName']: alias['agentAliasId'] for alias in agent_aliases}
                    selected_alias = st.selectbox("Select an alias to use:", options=list(alias_options.keys()))
                    alias_id = alias_options[selected_alias]
                    
                    # Chat interface
                    st.markdown("#### Conversation")
                    
                    # Display previous conversation
                    for message in st.session_state.test_conversation:
                        if message["role"] == "user":
                            st.markdown(
                                f"""
                                <div style="display:flex;justify-content:flex-end;margin-bottom:10px;">
                                    <div style="background-color:#ECEFF1;padding:10px;border-radius:10px;max-width:80%;">
                                        <p style="margin:0;"><strong>You:</strong> {message["content"]}</p>
                                    </div>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                        else:
                            st.markdown(
                                f"""
                                <div style="display:flex;justify-content:flex-start;margin-bottom:10px;">
                                    <div style="background-color:#E1F5FE;padding:10px;border-radius:10px;max-width:80%;">
                                        <p style="margin:0;"><strong>Agent:</strong> {message["content"]}</p>
                                    </div>
                                </div>
                                """, 
                                unsafe_allow_html=True
                            )
                    
                    # Input for new message
                    prompt = st.text_area("Enter your message to the agent:", height=100)
                    
                    if st.button("Send Message", key="send_message"):
                        if prompt:
                            # Add user message to conversation
                            st.session_state.test_conversation.append({"role": "user", "content": prompt})
                            
                            with st.spinner("Agent is thinking..."):
                                response = invoke_agent(bedrock_agent_runtime, agent_id, alias_id, prompt)
                            
                            if response:
                                # Add agent response to conversation
                                st.session_state.test_conversation.append({
                                    "role": "assistant", 
                                    "content": response.get('completion', 'No response')
                                })
                                
                                # Display trace information for debugging
                                if 'trace' in response and response['trace']:
                                    with st.expander("Response Trace (Debug)"):
                                        st.json(response['trace'])
                            
                            # Rerun to display updated conversation
                            st.rerun()
                        else:
                            st.warning("Please enter a message before sending.")
                    
                    # Option to clear conversation
                    if st.session_state.test_conversation and st.button("Clear Conversation", key="clear_conversation"):
                        st.session_state.test_conversation = []
                        st.rerun()
    
        else:
            st.error("Failed to load agent details. Please try again or select a different agent.")
    else:
        # Welcome screen when no agent is selected
        st.markdown(
            """
            <div class="dashboard-card">
                <h2 class="section-header">Welcome to the Agent Registry!</h2>
                <p>This dashboard helps you monitor, manage, and test your Amazon Bedrock Agents.</p>
                
                <div class="info-box">
                    <h4>Getting Started</h4>
                    <p>Select an agent from the sidebar to view detailed information, including:</p>
                    <ul>
                        <li>Agent configuration and capabilities</li>
                        <li>Associated action groups and knowledge bases</li>
                        <li>Interactive testing environment</li>
                        <li>Performance metrics and monitoring</li>
                    </ul>
                </div>
                
                <p>If you don't see any agents listed, make sure you have:</p>
                <ol>
                    <li>Created agents in your AWS account</li>
                    <li>Provided the correct AWS credentials</li>
                    <li>Selected the appropriate AWS region</li>
                </ol>
            </div>
            
            <div class="dashboard-card">
                <h3>Key Features</h3>
                <div class="flex-container">
                    <div class="metric-card" style="flex: 1;">
                        <h4>📊 Analytics</h4>
                        <p>Monitor your agents' performance with detailed metrics and usage patterns</p>
                    </div>
                    <div class="metric-card" style="flex: 1;">
                        <h4>🧪 Testing</h4>
                        <p>Test your agents directly within the dashboard using an interactive chat interface</p>
                    </div>
                    <div class="metric-card" style="flex: 1;">
                        <h4>🔍 Inspection</h4>
                        <p>Deep dive into agent configurations, action groups, and knowledge bases</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# Run the app
if __name__ == "__main__":
    main()