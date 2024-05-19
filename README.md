# Nirvana
<table>
  <tr>
    <td>
      <img src="https://github.com/Ernesto905/nirvana/assets/44984106/2efe2704-6de7-4bca-8194-569cd8cff32b" width="1500">
    </td>
    <td style="text-align: left; padding-left: 20px;">
      <b>Nirvana</b> is a platform tailored for enterprise professionals in managerial roles. With Nirvana, you can view your emails, generate actionable tasks, and gain insights from your data effortlessly. We provide essential tools for enterprises to automate the creation & updating of JIRA tasks directly from emails, improving productivity and efficiency.
    </td>
  </tr>
</table>

## Features

- Email Management: View your Gmail emails, mark important ones, and let Nirvana digest and record key information for future insights and analytics.
- Automated JIRA Actions: Generate JIRA actions directly from your emails with a single click. Nirvana intelligently analyzes your current JIRA and email contents to determine the appropriate actions using Snowflake's Arctic LLM.
- ChatNirvana Assistant: Interact with our assistant to ask questions about your data and generate visualizations. Powered by a ReAct Agent Workflow with a GPT-4o agent supervisor managing Snowflake Arctic sub-agents.
- Data Structuring: Utilizes the Arctic LLM's SQL generation capabilities to process and structure data into a personalized database.
- Enterprise Automation: Provides essential tools for enterprises to automate tasks directly from their emails, improving productivity and efficiency.

## Technologies Used
- Streamlit: For creating the frontend interface.
- Arctic LLM: Powers the AI and machine learning functionalities.
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
