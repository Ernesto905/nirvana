from wrappers import Arctic, GPT

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    PromptTemplate,
    FewShotPromptTemplate
)
from langchain_core.runnables import RunnableLambda
from operator import itemgetter

from pydantic import BaseModel, Field

_SYS_PROMPT = """
System: You are working for the software app Nirvana, which helps users (often managers of teams)
to manage their work and team members. Nirvana achieves this by providing a suite of tools and services, namely
a service that intakes emails that the user receives, and processes them to update or create Jira tickets or issues,
and provide other relevant insights if applicable.

Instructions:
"""

class Agent(BaseModel):
    """Abstraction for individual agents."""
    name: str
    description: str = Field(..., title="Description of the agent")

    def __str__(self):
        return self.name, self.description

class Chains:
    """Chains for each agent."""

    # Chain to directly query LLM
    vanilla_chain = (
        PromptTemplate.from_template(
            "{request}"
        )
        | Arctic()
        | StrOutputParser()
    )

    # Chain to select an agent
    # Given agent, request, options, spit out one of options
    router_chain = (
        PromptTemplate.from_template(
            _SYS_PROMPT +
            """
            You are a supervisor, tasked with managing user requests while having access to the
            following members on your team: {agents}.

            Given the following user request, classify it as being a request you could either fulfill yourself, or that
            one of your team members could better handle. 

            Select one of: {options}

            User Request: {request}
            """
        )
        | Arctic()
        | StrOutputParser()
    )

    # Chain to pick a table from a list of tables
    # Given a list of table name and description tuples, email, options, pick one of options
    table_picker_chain = (
        PromptTemplate.from_template(
            _SYS_PROMPT +
            """
            You are tasked with picking one or none of a list of tables that are most relevant to a given context.

            Tables: {tables}

            Given the following email, select one of the tables we may want to update given what is in the request. 
            If none of the tables are relevant, select 'NONE'.

            Select one of: {options}

            User Email: {email}
            """
        )
        | Arctic()
        | StrOutputParser()
    )

    # Chain to generate SQL code given a request and schema
    sql_generator_chain = (
        PromptTemplate.from_template(
            _SYS_PROMPT +
            """You are an expert data engineer that is very proficient in Postgres SQL. Given the following user request
            and the relevant table schema, generate the appropriate Postgres SQL code that would fulfill the user's request.

            Request: {request}

            Schema: {schema}

            Return only the SQL code that would fulfill the request, and nothing else, not even markdown code block triple backticks."""
        )
        | Arctic()
        | StrOutputParser()
    )

    # db_chain = (
    #     RunnableLambda(lambda x: f"Added {x} to the database.")
    # )

def select_agent(agents: list[Agent], request: str, selector: Arctic | GPT = Arctic):
    """
    Returns an agent among the list of agents that would be most
    suitable to execute the provided request.

    Assumptions:
    - Only ONE agent can be assigned to a request
    - Only ONE request is being handled at a time
    """
    options = ["SELF"] + [agent.name for agent in agents]

    print(agents)

    router_chain = (
        PromptTemplate.from_template(
            _SYS_PROMPT +
            f"""
            You are a supervisor, tasked with managing user requests while having access to the
            following members on your team: {agents}.

            Given the following user request, classify it as being a request you could either fulfill yourself, or that
            one of your team members could better handle. 

            Select one of: {options}"""
            + """
            User Request: {request}
            """
        )
        | selector()
        | StrOutputParser()
    )

    return router_chain.invoke({"request": request})

def get_table_context(table_name: str, email: str) -> dict:
    """
    Func that takes in a table and the user email, and 
    fetches the most relevant context from the table, if any.
    """

    return None

if __name__ == "__main__":

    email = """
        Subject: Revision Needed for Upcoming Release Specifications

        Hi Michael,

        I hope this message finds you well. As we approach the final stages of our current sprint, I've reviewed the specifications for the upcoming release and noticed some discrepancies that could affect our projected timeline and feature set.

        Specifically, the parameters for the new search functionality do not align with the initial requirements discussed in our last sprint planning meeting. This might lead to potential roadblocks for the QA team and impact the user experience.

        Could you please take a moment to review and adjust the relevant details? Ensuring these are in line with our objectives will be crucial for meeting our milestones without any delays.

        Thank you for looking into this at your earliest convenience.

        Best regards,

        Vanessa
        Software Development Team

    """

    # 1. TABLE-PICKER Agent: Given a list of table, table description tuples, and context, pick
    # one or none of the tables that are most relevant to the context.
    # if ONE -> return the table name, update that table (add row or edit row or delete row)
    # if NONE -> create a new table, infer the columns and table name
    # 2. FINDER Agent: Given some context and a table schema, find the most relevant data in the database
    # x. DECIDER Agent: Decide the operation to be performed on the database

    # given the email -> decide table
    table_info = [
        ("users", "A table that stores user information"),
        ("tickets", "A table that stores ticket information"),
        ("issues", "A table that stores issue information"),
        ("emails", "A table that stores email information"),
        ("projects", "A table that stores project information"),
        ("employees", "A table that stores information about employees on the team")
    ]

    # Chain that makes CRUD choice
    # Email -> Table Choice -> Extract relevant data -> CRUD choice
    crud_choice_chain = (
        {"tables": itemgetter("tables"), "options": itemgetter("options"), "email": itemgetter("email")}
        | Chains.table_picker_chain
        # | RunnableLambda(lambda x: get_table_context(x["table"], itemgetter("email")))
        # | RunnableLambda(lambda x: f"Added {x} to the database.")
    )

    print(crud_choice_chain.invoke({"email": email, "tables": table_info, "options": ["NONE"] + [table[0] for table in table_info]}))