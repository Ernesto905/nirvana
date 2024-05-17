from utils.wrappers import Arctic
from pydantic import BaseModel, Field

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    PromptTemplate,
    FewShotPromptTemplate
)
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.runnables import RunnableLambda
from ast import literal_eval

_SYS_PROMPT = """
System: You are working for the software app Nirvana, which helps users (often managers of teams)
to manage their work and team members. Nirvana achieves this by providing a suite of tools and services, namely
a service that intakes emails that the user receives, and processes them to update or create Jira tickets or issues,
and provide other relevant insights if applicable. Specifically, we offer the following services:
- Automated Jira ticket & issue creation or updates based on incoming email content
- Dynamic data aggregation from incoming emails storing important datapoints from emails and attachments
- Intelligent analysis, insights, and recommendations based on the stored data 

Instructions:
"""

class Agent(BaseModel):
    """Abstraction for individual agents."""
    name: str
    description: str = Field(..., title="Description of the agent")

    def __str__(self):
        return self.name, self.description

def dict_to_str(d: dict):
        return "\n".join([f"{k}: {v}" for k, v in d.items()])

"""
Chains:
- Chain for Email in -> Decision about what to do with JIRA out [output: md list that we can parse]
- Chain for Email + Decision in -> JIRA API call out (task / issue CRUD) [do this for every decision]
- Chain for Email + Decision in -> List of information we can store for later out [output: md list that we can parse]
- Chain for List of information in -> SQL query out
"""

# JIRA Features
def get_jira_actions(email: str, context: dict) -> dict:
    """
    Given an email, a set of options of what our backend can do with JIRA,
    and some context related to the user's current JIRA setup (projects, current issues, tasks, etc),
    we need to make a decision about what to do with the JIRA API, if anything.

    Assume context has the keys:
    - "projects": List of JIRA project names
    - "issues": List of JIRA issue keys
    - "tasks": List of JIRA task keys
    - "users": List of JIRA user keys
    """

    example_prompt = PromptTemplate(
        input_variables=["email", "context", "actions"],
        template="""
        Email: {email}
        Context: {context}
        Actions: {actions}
        """
    )

    examples = [{
        "email": """
        Subject: Urgent: Client Feedback on Project Falcon Deadline Adjustments
        From: Jane Doe janedoe@clientdomain.com
        Date: May 10, 2024
        To: John Smith johnsmith@yourcompany.com
        Dear John,
        I hope this message finds you well. Following our recent discussions and the revisions to the project timelines that were agreed upon, I wanted to confirm the new delivery dates for Project Falcon. As per our last meeting, the final deliverable is now expected by June 30, 2024, instead of the previously set date of July 20, 2024.
        Please acknowledge this email and update the project schedule accordingly. Additionally, we have noted some discrepancies in the last set of deliverables concerning the integration specifications. Could these be reviewed and addressed at the earliest?
        Looking forward to your prompt action on these matters.
        Best regards,
        Jane Doe
        Client Project Manager
        ClientDomain.com
            """,
        "context": """
        Project: Project Falcon
        Status: In Progress
        Key Issues:
        Falcon-101: Draft initial project deliverables (Due: May 25, 2024)
        Falcon-102: Review integration specifications (Due: June 10, 2024, Status: Pending Review)
        Falcon-103: Finalize all deliverables (Original Due Date: July 20, 2024)
        Epics:
        Epic-001: Infrastructure Setup
        Epic-002: Integration and Testing Phases
        """,
        "actions": """
        ["Update the due date of the task Falcon-103 to June 30, 2024, to reflect the new deadline communicated by the client.",
        "Create a new issue to address the discrepancies in the integration specifications mentioned by the client. Assign it to the relevant team member and prioritize it to ensure it's addressed before the next deliverable."]
        """
    }, 
    {
        "email": """
        Subject: 1:1 Meeting Agenda for May 12, 2024
        From: John Smith
        Date: May 10, 2024
        To: Team Members
        Hi Team,
        I hope you're all doing well. I'd like to remind you about our upcoming 1:1 meetings scheduled for May 12, 2024. Please review the agenda items below and come prepared to discuss your progress, challenges, and any support you may need.
        Agenda:
        1. Project Updates
        2. Roadblocks and Challenges
        3. Support Needed
        4. Any Other Business
        Please confirm your availability for the meeting and let me know if you have any specific topics you'd like to discuss.
        Looking forward to our discussions.
        Best,
        John
        """,
        "context": """
        Project: Arctic Development
        Status: Ongoing
        Key Issues:
        Arctic-221: Implement User Authentication (Due: May 15, 2024)
        Arctic-232: Design Database Schema (Due: May 20, 2024) 
        Project: Mobile App Launch
        Status: Pending
        Key Issues:
        Mobile-101: Finalize UI Design (Due: May 30, 2024)
        Mobile-102: Implement Push Notifications (Due: June 5, 2024)
        """,
        "actions": """
            NONE
        """
    }
    ]

    prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        input_variables=["email", "context"],
        suffix="Email: {email}\nContext: {context}\nActions:",
        prefix=_SYS_PROMPT + """
        Given the below email that the user just received, and some context in the user's JIRA,
        what are some helpful actions that we can take with JIRA based on the email content? Identify
        possible actions based on action items, deadlines, assignments, and other relevant information in the email,
        and return a Python list of the different actions we should take. Note that creating
        entire projects is out of scope for this task. We are only concerned with the following actions:
        - Creating new issues (epics, tasks, or sub-tasks) 
            - Setting assignees, due dates, and labels
        - Updating existing issues in the following ways:
            - Changing issue status (TO DO, IN PROGRESS, DONE)
            - Changing issue assignee
            - Changing due dates
            - Change labels

        If there are no actions to take, return "NONE". Otherwise, return a Python formatted list of the actions, such that the actions
        are dictionaries.
        The actions should only be actions that are specific and actionable in JIRA.
        """
    )

    # convert context to str because replicate api does not take kindly to curly braces!!!!!!!
    context = dict_to_str(context)

    chain = (
        prompt
        | Arctic()
        | StrOutputParser()
    )

    result = chain.invoke({"email": email, "context": context})

    if result.strip().upper() == "NONE":
        output = []
    else:
        output = literal_eval(result)

    return {"actions": output}

def get_jira_api_call(email: str, decision: str, context: dict):
    """
    Given an email, a decision about what to do with JIRA, and context related to the user's JIRA setup,
    we need to make a JIRA API call to create or update a JIRA issue or task.

    Assume context has the keys:
    - "projects": List of JIRA project names
    - "issues": List of JIRA issue keys
    - "tasks": List of JIRA task keys
    - "users": List of JIRA user keys
    """

    prefix: str = """
    You are an assistant working on the JIRA integration module of the Nirvana app.
    A user has given us an email, and we have already made a decision about a specific action to take
    in JIRA based on the email content. Now, we need to make the actual API call to JIRA to perform 
    this action. This call will be formatted as a Python function call that will be executed to interact with the JIRA API.

    We have access to the following functions to interact with the JIRA API:
    - create_issue(project, summary, description, assignee, priority)
    - update_issue(issue_key, summary, description, assignee, priority)
    - create_task(issue_key, summary, description, assignee, priority)
    - update_task(task_key, summary, description, assignee, priority)

    Given the below email, the specific action to take in JIRA, and the context of the user's JIRA setup,
    return the Python function call that corresponds to the action to be taken in JIRA. If the action is to create a new issue or task,
    include the necessary parameters (project, summary, description, assignee, priority). If the action is to update an existing issue or task,
    include the issue_key or task_key along with the updated parameters. The other parameters can be left as None if they are not relevant to the action.
    """

    example_prompt = PromptTemplate(
        input_variables=["email", "decision", "context", "api_call"],
        template="""
        Email: {email}
        Context: {context}
        Decision: {decision}
        API Call: {api_call}
        """
    )

    examples = [{
        "email": """
        Subject: Urgent: Client Feedback on Project Falcon Deadline Adjustments
        From: Jane Doe janedoe@clientdomain.com
        Date: May 10, 2024
        To: John Smith johnsmith@yourcompany.com
        Dear John,
        I hope this message finds you well. Following our recent discussions and the revisions to the project timelines that were agreed upon, I wanted to confirm the new delivery dates for Project Falcon. As per our last meeting, the final deliverable is now expected by June 30, 2024, instead of the previously set date of July 20, 2024.
        Please acknowledge this email and update the project schedule accordingly. Additionally, we have noted some discrepancies in the last set of deliverables concerning the integration specifications. Could these be reviewed and addressed at the earliest?
        Looking forward to your prompt action on these matters.
        Best regards,
        Jane Doe
        Client Project Manager
        ClientDomain.com
        """,
        "context": """
        Project: Project Falcon
        Status: In Progress
        Key Issues:
        Falcon-101: Draft initial project deliverables (Due: May 25, 2024)
        Falcon-102: Review integration specifications (Due: June 10, 2024, Status: Pending Review)
        Falcon-103: Finalize all deliverables (Original Due Date: July 20, 2024)
        Epics:
        Epic-001: Infrastructure Setup
        Epic-002: Integration and Testing Phases
        """,
        "decision": """
        Update the due date of the task Falcon-103 to June 30, 2024, to reflect the new deadline communicated by the client.
        """,
        "api_call": """
        update_task('Falcon-103', None, None, None, None, '2024-06-30')
        """}
    ]

    prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        input_variables=["email", "decision", "context"],
        suffix="Email: {email}\nDecision: {decision}\nContext: {context}\nAPI Call:",
        prefix=prefix
    )

    context = dict_to_str(context)

    chain = (
        prompt 
        | Arctic()
        | StrOutputParser()
    )

    output = chain.invoke({"email": email, "decision": decision, "context": context})

    return {"api_call": output}

# Unified Database Features
def extract_features(email: str, schema: str) -> dict:
    """
    Given an email, and what our current database looks like, we need to decide what information to extract
    and remember from the email for later analysis or use as far as recommendations or insights in the app go.

    Assume context has the keys:
    - "projects": List of JIRA project names
    - "issues": List of JIRA issue keys
    - "tasks": List of JIRA task keys
    - "users": List of JIRA user keys
    """

    prefix = """
    You are an assistant working on the data aggregation and analysis module of the Nirvana app. 
    Your task is to extract relevant information from the incoming email and store it in the database for future analysis and insights. 
    This involves identifying key data points from the email, deciding what would be relevant for providing future recommendations or insights,
    and storing this information in the database based on the provided schema. Note that data about projects, issues, tasks, and users are already stored in the database, so specific JIRA-related information should not be extracted as it would be redundant.
    Rather, focus on extracting details from the emails, such as dates, names, changes, patterns, or any other relevant information that could be useful for future analysis or recommendations.
    We are also interested in making observations about people, dates, and other entities mentioned in the email that could be relevant for future insights.

    Given the below email, and what our database currently looks like,
    return a list of SQL statements that will be executed consecutively to store the extracted information in the database.
    Be mindful of existing tables. If a table does not exist and you believe we should create it (and, critically, that it will be useful later!), create it. 
    If a table needs to be modified, modify it.
    The SQL statements should be valid and executable, and will be executed in the order you provide them.

    Return the statements in Python strings in a Python list. If no information needs to be stored, return an empty list.
    """

    example_prompt = PromptTemplate(
        input_variables=["email", "schema", "extracted_information"],
        template="""
        Email: {email}
        Schema: {schema}
        Extracted Information: {extracted_information}
        """
    )

    examples = [{
        "email": """
        Subject: Urgent: Client Feedback on Project Falcon Deadline Adjustments
        From: Jane Doe janedoe@clientdomain.com
        Date: May 10, 2024
        To: John Smith johnsmith@yourcompany.com
        Dear John,
        I hope this message finds you well. Following our recent discussions and the revisions to the project timelines that were agreed upon, I wanted to confirm the new delivery dates for Project Falcon. As per our last meeting, the final deliverable is now expected by June 30, 2024, instead of the previously set date of July 20, 2024.
        Please acknowledge this email and update the project schedule accordingly. Additionally, we have noted some discrepancies in the last set of deliverables concerning the integration specifications. Could these be reviewed and addressed at the earliest?
        Looking forward to your prompt action on these matters.
        Best regards,
        Jane Doe
        Client Project Manager
        ClientDomain.com
            """,
        "schema": """
        Table: Client Feedback
        Columns:
        - sender: VARCHAR(255)
        - date: DATE
        - subject: VARCHAR(255)
        - message: TEXT
        - recipient: VARCHAR(255)
        """,
        "extracted_information": """
        ["INSERT INTO Client_Feedback (sender, date, subject, message, recipient) VALUES ('
        Jane Doe', '2024-05-10', 'Urgent: Client Feedback on Project Falcon Deadline Adjustments',
        'Following our recent discussions and the revisions to the project timelines that were agreed upon, I wanted to confirm the new delivery dates for Project Falcon. As per our last meeting, the final deliverable is now expected by June 30, 2024, instead of the previously set date of July 20, 2024. Please acknowledge this email and update the project schedule accordingly. Additionally, we have noted some discrepancies in the last set of deliverables concerning the integration specifications. Could these be reviewed and addressed at the earliest? Looking forward to your prompt action on these matters. Best regards, Jane Doe Client Project Manager ClientDomain.com', 'John Smith')",
        "CREATE TABLE IF NOT EXISTS Date_Changes (date DATE, project VARCHAR(255), new_date DATE, previous_date DATE)",
        "INSERT INTO Date_Changes (date, project, new_date, previous_date) VALUES ('2024-05-10', 'Project Falcon', '2024-06-30', '2024-07-20')",
        ]
        """
    }, 
    {
        "email": """
        Subject: Revised Budget Estimates for Project Mercury
        From: Alice Johnson alicejohnson@vendor.com
        Date: May 15, 2024
        To: Sara White sarawhite@yourcompany.com
        Hello Sara,
        After reviewing the latest project requirements and consulting with our finance department, we've come up with a revised budget for Project Mercury. The total budget now stands at $320,000, which is a 15% increase from the original estimate of $280,000 due to additional licensing fees.
        Please find attached the detailed budget breakdown and let us know if there are any further adjustments needed.
        Thank you for your cooperation.
        Best,
        Alice Johnson
        Account Manager
        Vendor.com
        """,
        "schema": """
        Table: Project Budgets
        Columns:
        - sender: VARCHAR(255)
        - date: DATE
        - project: VARCHAR(255)
        - original_budget: DECIMAL(10, 2)
        - revised_budget: DECIMAL(10, 2)
        - message: TEXT
        - recipient: VARCHAR(255)
        """,
        "extracted_information": """
        ["INSERT INTO Project_Budgets (sender, date, project, original_budget, revised_budget, message, recipient) VALUES ('
        Alice Johnson', '2024-05-15', 'Project Mercury', 280000, 320000,
        'After reviewing the latest project requirements and consulting with our finance department, we've come up with a revised budget for Project Mercury. The total budget now stands at $320,000, which is a 15% increase from the original estimate of $280,000 due to additional licensing fees. Please find attached the detailed budget breakdown and let us know if there are any further adjustments needed. Thank you for your cooperation. Best, Alice Johnson Account Manager Vendor.com', 'Sara White')",
        "CREATE TABLE IF NOT EXISTS Budget_Changes (date DATE, project VARCHAR(255), original_budget DECIMAL(10, 2), revised_budget DECIMAL(10, 2))",
        "INSERT INTO Budget_Changes (date, project, original_budget, revised_budget) VALUES ('2024-05-15', 'Project Mercury', 280000, 320000)",
        ]
        """
    }]

    prompt = FewShotPromptTemplate(
        examples=examples,
        example_prompt=example_prompt,
        input_variables=["email", "schema"],
        suffix="Email: {email}\nSchema: {schema}\nExtracted Information:",
        prefix=prefix
    )

    chain = (
        prompt
        | Arctic()
        | StrOutputParser()
    )

    # print("Given email:", email)
    # print("Schema:", schema)

    try:
        output = chain.invoke({"email": email, "schema": schema})
    except Exception as e:
        print("Error with feature extraction chain invocation:", e)
        output = []
    # print("Output:", output)

    return {"extracted_information": literal_eval(output)}

# Misc
def generate_sql(request: str, schema: str) -> dict:
    prompt = PromptTemplate.from_template(
        """
        You are a professional data engineer working on the data analysis module of the Nirvana app.

        Given the below user request, as well as what our current database tables and columns look like,
        generate the appropriate SQL query, if applicable, to retrieve relevant data from the database.

        Note that we are working inside a PostgreSQL database, within a schema, so
        your queries should look like "SELECT * FROM information_schema.columns WHERE table_name = 'table_name'" instead of
        "SELECT * FROM table_name".

        If the request does not require a SQL query, return "No SQL query needed".

        Request: {request}

        Schema: {schema}
        """
    )

    chain = (
        prompt
        | Arctic()
        | StrOutputParser()
    )

    output = chain.invoke({"request": request, "schema": schema})

    return {"sql_query": output}

def route_agent(self, message: str, agents: list[Agent]) -> dict:
    options = ["SELF"] + [agent.name for agent in agents]

    chain = (
        PromptTemplate.from_template(
            _SYS_PROMPT + f"""
            You are a supervisor, tasked with managing user requests while having access to the
            following members on your team: {agents}.

            Given the following user request, classify it as being a request you could either fulfill yourself, or that
            one of your team members could better handle.

            Select one of: {options}
            """
            + """
            Request: {message}
            """
        )
        | Arctic()
        | StrOutputParser()
    )

    return chain.invoke({"message": message})

# def function_call(request: str, functions: list[str]) -> dict:
#     """
#     Given an email and a list of functions, return the correct function call, if any.
#     """

#     prefix: str = f"""
#     You are an assistant working on the JIRA integration module of the Nirvana app.
#     A user has given us an email, and we a set of functions available to us. 
#     We have to make a decision about which functions (could be 0, one, or multiple) to use. 
#     This call will be formatted as a Python function call that will be executed.

#     We have access to the following functions:
#     {functions}

#     Given the below email and a list of functions, return the Python function call that corresponds to the action to be taken.
#     If the function has required parameters, include them in the function call. If the function has
#     optional parameters, you can include them if you think they are relevant to the action to be taken. Return
#     the function call, or calls, as a list of Python strings where each string is a Python function call.
#     """

#     example_prompt = PromptTemplate(
#         input_variables=["email", "functions", "function_call"],
#         template="""
#         Email: {email}
#         Functions: {functions}
#         Function Call: {function_call}
#         """
#     )

#     ...

class Function(BaseModel):
    string: str = Field(..., title="The function and its parameters as a Python function call string")
    description: str = Field(..., title="Description of the function")

    def __str__(self):
        return self.string, self.description

class ChatArctic:
    def __init__(self):
        self.model = Arctic()

        plotter_agent = Agent(name="Plotter", description="Agent that can retrieve and plot data from the database - use if the user asks for data visualization.")
        sql_agent = Agent(name="SQL Query", description="Agent that can generate SQL queries based on user requests and the database schema - use if the user is asking for something specific about the data.")

        self.agents = [
            plotter_agent,
            sql_agent
        ]

    def invoke(self, message: str) -> str:

        def route(x: dict) -> dict:
            if x["route"] == "SELF":
                return (
                    PromptTemplate.from_template(
                        _SYS_PROMPT + """
                        {request}
                        """
                    )
                    | Arctic()
                    | StrOutputParser()
                )
            else:
                agent = x["route"]
                print("Agent selected:", agent)

                if agent == "Plotter":
                    ...
                elif agent == "SQL Query":
                    ...
                else:
                    # TODO: in the future automatically pick closest levenshtein distance agent
                    raise ValueError(f"Invalid agent {agent} selected.")

        chain = (
            # first step of chain:
            # given what the current database looks like, make a decision about whether we need to use one of the
            # agents or if the request is something else like a trivial or question or maybe something out of scope
            RunnableLambda(lambda x: {"route" : route_agent(x, self.agents)})
            # second step of chain:
            # given the decision, route the message to the appropriate agent
            | RunnableLambda(route)
        )

        # return self.model.invoke(message)
        return chain.invoke(message.content)

if __name__ == "__main__":

    email = """
        Subject: Urgent: High Latency Issue Detected in Ride API

        From: system_monitoring@ridecompany.com

        Date: May 10, 2024, 09:15 AM

        To: john.doe@ridecompany.com

        Dear John,

        We have detected an unexpected spike in latency on the Ride API today at 08:45 AM, with response times exceeding 500ms, which is beyond the acceptable threshold of 200ms. This issue appears to be impacting multiple endpoints, particularly those handling ride booking requests.

        Initial Findings:

        The latency spike correlates with a significant increase in ride booking requests.
        Preliminary logs indicate possible database bottlenecks.
        Impact:

        Increased customer complaints about app responsiveness.
        Potential drop in user satisfaction and increased churn risk.
        Please address this as a priority.

        Best Regards,
        System Monitoring Team
        Ride Company
    """

    context = {
        "projects": ["Ride Operations", "API Development", "Customer Service Platform"],
        "issues": ["Ride-142: Ride API Latency Over 300ms Last Quarter", 
                   "Ride-198: Database Optimization for Scalability", 
                   "CUST-77: Customer Complaints on App Responsiveness"],
        "recent updates": ["RIDE-198 updated yesterday with new DB schema proposals.",
                           "CUST-77 has a scheduled review today to discuss recent feedback trends."],
        "users": ["john.doe", "jane.smith", "admin"]
    }

    actions = get_jira_actions(email, context)

    print("==Suggested actions==\n\n", actions["actions"])

    for action in actions["actions"]:
        api_call = get_jira_api_call(email, action, context)
        print("API Call:", api_call["api_call"])

    # extracted_info = extract_features(email, """
    #     Table: System Alerts
    #     Columns:
    #     - sender: VARCHAR(255)
    #     - date: DATE
    #     - subject: VARCHAR(255)
    #     - message: TEXT
    #     - recipient: VARCHAR(255)
    #     - impact: TEXT
    #     - findings: TEXT
    # """)
    # print("==Extracted Information==\n\n", extracted_info["extracted_information"])
