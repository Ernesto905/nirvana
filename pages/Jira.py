import streamlit as st
from jira.authentication import get_authorization_url, get_access_token

# Streamlit app
# def main():
#     st.title("Jira OAuth 2.0")
#
#     authenticated = st.session_state.get("authenticated", False)
#     authorization_url, state = get_authorization_url()
#
#     if not authenticated: 
#         auth_button = st.link_button("Authenticate Jira", authorization_url)
#         code = st.query_params["code"]
#         if auth_button: 
#             st.session_state['auth_state'] = state
#             st.rerun()
#         if code: 
#
#
#     if authenticated:
#         print("Good job!")

    # # Check if the user has already authenticated
    # if 'access_token' not in st.session_state:
    #     if 'auth_state' not in st.session_state:
    #
    #         authorization_url, state = get_authorization_url()
    #         st.session_state['auth_state'] = state
    #         auth_button = st.link_button(url=authorization_url, label=":sunglasses:")
    #         if auth_button:
    #             # authorization_url, state = get_authorization_url()
    #             st.session_state['auth_state'] = state
    #             # st.write(f"{authorization_url}")
    #             st.rerun()
    #     else:
    #         # Check if the user has been redirected back with the authorization code
    #         print("Query params are", st.query_params)
    #         code = st.query_params().get('code', [None])[0]
    #         state = st.query_params().get('state', [None])[0]
    #
    #         
    #         print("Code is: ", code, "\nAnd state is", state)
    #         if code and state == st.session_state['auth_state']:
    #             # Exchange the authorization code for an access token
    #             access_token = get_access_token(code)
    #             st.session_state['access_token'] = access_token
    #             print("We have obtained access token: ", access_token)
    #             st.rerun()
    # else:
    #     # User has already authenticated
    #     access_token = st.session_state['access_token']
    #     st.write("You are authenticated!")
    #     # Use the access_token to make API requests to Jira
    #     # ...

def main():
    # Check if the user has already authenticated
    if 'access_token' not in st.session_state:
        # Display the login button
        authorization_url, state = get_authorization_url()

        auth_button = st.link_button("Authenticate Jira", authorization_url)

        if auth_button:
            # Generate the authorization URL
            st.session_state['auth_state'] = state

            # Open the authorization URL in a new browser tab/window
            # webbrowser.open_new_tab(authorization_url)
    else:
        st.success("Successfully Authenticated")
        # User is already authenticated
        access_token = st.session_state['access_token']
        # Use the access token to make API requests to Jira
        # ...

    # Add a callback route to handle the redirect from Jira
    if 'code' in st.query_params:
        # Retrieve the authorization code from the query parameters
        authorization_code = st.query_params['code']

        # Exchange the authorization code for an access token
        access_token = get_access_token(authorization_code)

        # Store the access token in the session state
        st.session_state['access_token'] = access_token

        # Remove the authorization code from the URL
        st.query_params.clear()

        # Rerun the app
        st.rerun()


if __name__ == '__main__':
    main()
