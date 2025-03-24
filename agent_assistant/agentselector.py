import boto3
import json
import numpy as np
from typing import Dict, List, Any, Optional
from botocore.exceptions import ClientError
from uuid import uuid4

class BedrockAgentSelector:
    def __init__(self, region: str = "us-west-2"):
        self.bedrock_agent = boto3.client('bedrock-agent', region_name=region)
        self.bedrock_runtime = boto3.client('bedrock-runtime', region_name=region)
        self.bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=region)

        self.agents_cache = None
        self.embedding_model = 'amazon.titan-embed-text-v2:0'
        self.agent_embeddings = {}
        
    def get_all_agents(self, refresh_cache: bool = False) -> List[Dict[str, Any]]:
        if self.agents_cache is not None and not refresh_cache:
            return self.agents_cache
            
        agents = []
        paginator = self.bedrock_agent.get_paginator('list_agents')
        
        # Paginate through all agents
        for page in paginator.paginate():
            for agent_summary in page.get('agentSummaries', []):
                agent_id = agent_summary.get('agentId')
                agentName = agent_summary.get('agentName')

                agent_response = self.bedrock_agent.get_agent(agentId=agent_id)
                agent_info = agent_response['agent']

                # Extract relevant information
                agent_details = {
                    'name': agent_info.get('agentName'),
                    'agentId': agent_info.get('agentId'),
                    'instructions': agent_info.get('instruction'),
                    'status': agent_info.get('agentStatus'),
                    'foundation_model': agent_info.get('foundationModel'),
                    'created_at': agent_info.get('creationDateTime'),
                    'last_updated': agent_info.get('lastUpdatedDateTime'),
                    'aliases': [],
                    'defaultAliasId' : ''
                }
                alias_response = self.bedrock_agent.list_agent_aliases(agentId=agent_id)
                agent_details['aliases'] = alias_response.get('agentAliasSummaries', [])
                if agent_details['aliases']:
                    latest_alias = max(agent_details['aliases'], key=lambda x: x['updatedAt'])
                    agent_details['defaultAliasId'] = latest_alias['agentAliasId']
                else:
                    agent_details['defaultAliasId'] = None
                    
                agents.append(agent_details)
        
        self.agents_cache = agents
        return agents
    
    def _get_embedding(self, text: str) -> np.ndarray:
        try:
            response = self.bedrock_runtime.invoke_model(
                modelId=self.embedding_model,
                body=json.dumps({"inputText": text})
            )
            embedding = json.loads(response.get("body").read())["embedding"]
            return np.array(embedding)
        except Exception as e:
            print(f"Error getting embedding: {e}")
            # Return zero vector as fallback
            return np.zeros(1536)
    
    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        
        if norm_v1 == 0 or norm_v2 == 0:
            return 0
            
        return np.dot(v1, v2) / (norm_v1 * norm_v2)
    
    def _create_agent_embeddings(self):
        """Create embeddings for all agents based on their descriptions and instructions."""
        agents = self.get_all_agents()
        
        for agent in agents:
            # Create a rich representation of the agent
            self.agent_embeddings[agent['agentId']] = self._get_embedding(agent['instructions'])
    
    def _semantic_match(self, query: str) -> Dict:
        # Ensure we have agent embeddings
        if not self.agent_embeddings:
            self._create_agent_embeddings()
            
        agents = self.get_all_agents()
        query_embedding = self._get_embedding(query)
        
        print(f""" found {len(agents)} agents""")

        similarities = []
        for agent in agents:
            agent_id = agent["agentId"]
            if agent_id in self.agent_embeddings:
                similarity = self._cosine_similarity(query_embedding, self.agent_embeddings[agent_id])
                similarities.append({
                    "agent": agent,
                    "score": similarity
                })
        
        # Find the agent with the highest similarity
        best_match = max(similarities, key=lambda x: x["score"]) if similarities else {"agent": None, "score": 0}
        print(f""" {best_match['agent']['name']} will help with the request""")
        return best_match
    
    def select_agent(self, query: str, threshold: float = 0.6) -> Dict:
        match_result = self._semantic_match(query)
        
        best_agent = match_result["agent"]
        confidence = match_result["score"]

        print(best_agent["agentId"])
        print(best_agent["defaultAliasId"])

        return best_agent
    
    def invoke_agent(self, best_agent, query):
        agentResponse = self.bedrock_agent_runtime.invoke_agent(
            agentId=best_agent["agentId"],
            agentAliasId=best_agent["defaultAliasId"],  # Changed from aliasId to agentAliasId
            sessionId=str(uuid4()),  # Generate a unique session ID
            inputText=query,  # The actual prompt/question for the agent
        )

        # Process the completion stream
        full_response = ""
        for event in agentResponse['completion']:
            if 'chunk' in event:
                chunk = event['chunk']
                if 'bytes' in chunk:
                    full_response += chunk['bytes'].decode()

        # You might want to return both the response and the confidence score
        return {
            "response": full_response,
            "agent_id": best_agent["agentId"]
        }