# Nirvana
<table>
  <tr>
    <td>
      <img src="https://github.com/Ernesto905/nirvana/assets/44984106/2efe2704-6de7-4bca-8194-569cd8cff32b" width="1500">
    </td>
    <td style="text-align: left; padding-left: 20px;">
      Nirvana is a Flask REST API tailored for enterprise professionals in managerial roles. Enterprises can set up the API to generate insights from and take actions in JIRA based on emails. The Nirvana API provides essential tools for enterprises to automate the creation and updating of JIRA tasks directly from emails, improving productivity and efficiency.
    </td>
  </tr>
</table>

## Features

- Automated JIRA Actions: Generate JIRA actions directly from your emails. Nirvana intelligently analyzes your current JIRA and email contents to determine the appropriate actions using Snowflake's Arctic LLM.
- ChatNirvana Assistant: Interact with our assistant to ask questions about data aggregate in the Nirvana Postgres DB and generate visualizations. Powered by a ReAct Agent Workflow with a GPT-4o agent supervisor managing Snowflake Arctic sub-agents.
- Data Structuring: Utilizes the Arctic LLM's SQL generation capabilities to process and structure data from your emails into the Nrivana Postgres DB.
- Enterprise Automation: Provides essential tools for enterprises to automate tasks directly from their emails, improving productivity and efficiency.

## API Endpoints
- POST v1/data: Process an email and store relevant information from the email into the Nirvana DB. This process occurs with user-based data isolation.
- POST v1/jira/action: Generate actions to take in JIRA based on a provided email.
- POST v1/jira/execute: Given an action to take in JIRA, (expected in the output format of v1/jira/action) actually execute that action and update JIRA.
- POST v1/chat: Chat with ChatNirvana about the data stored in Nirvana DB. ChatNirvana can answers questions about the data, and generate visualizations (returned in a base64 encoded format inside a <img> tag).

## Technologies Used
- Arctic & GPT-4o LLM: Powers the AI and machine learning functionalities.
- AWS: Ensures scalability and robustness in data handling and storage.
- Postgres: Manages all database operations.
- Flask: Serves as the backend framework.
- Google Workspaces: Integrates emailing solutions.
- Jira: Manages project and issue tracking.

## Architecture Overview
Nirvana is built around a comprehensive RESTful API that encapsulates its core functionalities. The platform's architecture ensures seamless integration between the frontend and backend, providing a smooth user experience.

### Frontend
- Streamlit Dashboard: Serves as the user interface for demonstrating Nirvana’s capabilities.
### Backend
- RESTful API: Provides endpoints for email management, JIRA action generation, data interaction, and more.
- Email Processing: Ingests and analyzes emails to extract and record important information.
- JIRA Integration: Automates task creation and updates based on email content.
- Data Interaction: Allows users to chat with ChatNirvana, generating insights and visualizations from ingested data.

By automating routine tasks, providing actionable insights, and enhancing productivity through intelligent data processing and interaction.
