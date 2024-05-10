from wrappers import Arctic
from pydantic import BaseModel, Field

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    PromptTemplate,
    FewShotPromptTemplate
)
from langchain_core.runnables import RunnableLambda
from operator import itemgetter

_SYS_PROMPT = """
System: You are working for the software app Nirvana, which helps users (often managers of teams)
to manage their work and team members. Nirvana achieves this by providing a suite of tools and services, namely
a service that intakes emails that the user receives, and processes them to update or create Jira tickets or issues,
and provide other relevant insights if applicable. Specifically, we offer the following services:
- Automated Jira ticket & issue creation or updates based on incoming email content
- Intelligent insights and recommendations based on the user's Jira setup and incoming emails
- Dynamic data aggregation from incoming emails storing important datapoints from emails and attachments

Instructions:
"""

class Agent(BaseModel):
    """Abstraction for individual agents."""
    name: str
    description: str = Field(..., title="Description of the agent")

    def __str__(self):
        return self.name, self.description

"""
Chains:
- Chain for Email in -> Decision about what to do with JIRA out [output: md list that we can parse]
- Chain for Email + Decision in -> JIRA API call out (task / issue CRUD) [do this for every decision]
- Chain for Email + Decision in -> List of information we can store for later out [output: md list that we can parse]
- Chain for List of information in -> SQL query out
"""

def get_jira_actions(email: str, context: dict):
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
        - Update the due date of the task Falcon-103 to June 30, 2024, to reflect the new deadline communicated by the client.
        - Create a new issue to address the discrepancies in the integration specifications mentioned by the client. Assign it to the relevant team member and prioritize it to ensure it's addressed before the next deliverable.
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
        and return a markdown list of the different actions we should take. Note that creating
        entire projects is out of scope for this task. We are only concerned with updating or creating
        epics, issues, and tasks, and assigning them to the appropriate team members.

        If there are no actions to take, return "NONE". Otherwise, return a markdown formatted list of the actions.
        The actions should only be actions that are specific and actionable in JIRA.
        """
    )   

    # convert context to str because replicate api does not take kindly to curly braces!!!!!!!
    def dict_to_str(d: dict):
        return "\n".join([f"{k}: {v}" for k, v in d.items()])

    context = dict_to_str(context)

    chain = (
        prompt
        | Arctic()
        | StrOutputParser()
    )

    return chain.invoke({"email": email, "context": context})

def get_jira_api_call(email: str, decision: str, context: dict = {}):
    """
    Given an email, a decision about what to do with JIRA, and perhaps some context related to the user's JIRA setup,
    we need to make a JIRA API call to create or update a JIRA issue or task.

    Assume context has the keys:
    - "projects": List of JIRA project names
    - "issues": List of JIRA issue keys
    - "tasks": List of JIRA task keys
    - "users": List of JIRA user keys
    """

    chain = (
        PromptTemplate.from_template(
            _SYS_PROMPT + """
                balling
            """
        )
        | Arctic()
        | StrOutputParser()
    )

    return chain.invoke({"email": email, "decision": decision, "context": context})

def extract_information(email: str, decision: str, context: dict = {}):
    """
    Given an email, a decision about what to do with JIRA, and perhaps some context related to the user's JIRA setup,
    we need to extract relevant information from the email to store for later use.

    Assume context has the keys:
    - "projects": List of JIRA project names
    - "issues": List of JIRA issue keys
    - "tasks": List of JIRA task keys
    - "users": List of JIRA user keys
    """

    chain = (
        PromptTemplate.from_template(
            _SYS_PROMPT + """
                Given the below email that the user just received, and some context in the user's JIRA,
                is there any information that we can extract for later analysis or use as far as 
                recommendations or insights in the app go?

                Email: {email}

                Context: {context}

                If there is information to extract, return a markdown list of the information.
                Otherwise, return "NONE".
            """
        )
        | Arctic()
        | StrOutputParser()
    )

    return chain.invoke({"email": email}, {"context": context})

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

    print(get_jira_actions(email, context))