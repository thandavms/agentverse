# Agent Registry Dashboard

A streamlit web application for managing and monitoring Amazon Bedrock Agents.

## 🌟 Features

- **Agent Management**: View and manage all your Bedrock agents in one place
- **Interactive Testing**: Test agents through an intuitive chat interface
- **Detailed Analytics**: Monitor agent performance with built-in metrics
- **Knowledge Base Integration**: View and manage associated knowledge bases
- **Action Group Management**: Monitor and inspect agent action groups
- **Secure Authentication**: AWS credentials management with environment variables

## 📋 Prerequisites

- Python 3.7+
- AWS Account with Bedrock access
- Required AWS credentials and permissions
- Streamlit

## 🔧 Installation

1. Clone the repository
2. Install the required dependencies:
```bash
pip install streamlit boto3 pandas plotly python-dotenv
```
## 🚀 Usage

### Set up your environment variables:

```python
ACCESS_KEY=your_aws_access_key
SECRET_KEY=your_aws_secret_key
AWS_REGION=your_preferred_region

```

### Start the application

```python
streamlit run agentregistry.py
```

Access the dashboard through your web browser (typically http://localhost:8501)

If environment variables aren't set, provide AWS credentials through the secure input fields in the sidebar




