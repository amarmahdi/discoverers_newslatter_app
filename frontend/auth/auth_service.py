import os
import json
from python_graphql_client import GraphqlClient

# URL for the GraphQL API (local server)
API_URL = "http://localhost:8000/graphql/"

class AuthService:
    """Service to handle authentication with the GraphQL backend"""
    
    def __init__(self):
        self.client = GraphqlClient(endpoint=API_URL)
        self.token_file = os.path.join(os.path.dirname(__file__), "auth_token.json")
        self._token = None
        self._user = None
        self._load_token()
    
    def _load_token(self):
        """Load the auth token from a file if it exists"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, "r") as f:
                    data = json.load(f)
                    self._token = data.get("token")
                    self._user = data.get("user")
        except Exception:
            # If there's any error, reset the token
            self._token = None
            self._user = None
    
    def _save_token(self):
        """Save the auth token to a file"""
        if self._token and self._user:
            with open(self.token_file, "w") as f:
                json.dump({
                    "token": self._token,
                    "user": self._user
                }, f)
    
    def _clear_token(self):
        """Clear the saved token"""
        self._token = None
        self._user = None
        if os.path.exists(self.token_file):
            os.remove(self.token_file)
    
    def login(self, email, password):
        """Login with email and password via GraphQL"""
        login_mutation = """
        mutation Login($email: String!, $password: String!) {
            tokenAuth(email: $email, password: $password) {
                token
                payload
            }
        }
        """
        
        variables = {
            "email": email,
            "password": password
        }
        
        try:
            result = self.client.execute(query=login_mutation, variables=variables)
            
            if "errors" in result:
                return False, result["errors"][0]["message"]
            
            token_data = result.get("data", {}).get("tokenAuth", {})
            if token_data and "token" in token_data:
                self._token = token_data["token"]
                
                # Get user info
                self._fetch_user_info()
                self._save_token()
                return True, "Login successful"
            
            return False, "Invalid credentials"
        
        except Exception as e:
            return False, f"Login error: {str(e)}"
    
    def _fetch_user_info(self):
        """Fetch the user information after login"""
        if not self._token:
            return
        
        me_query = """
        query {
            me {
                id
                email
                firstName
                lastName
                role
            }
        }
        """
        
        headers = {"Authorization": f"JWT {self._token}"}
        
        try:
            result = self.client.execute(query=me_query, headers=headers)
            if "data" in result and "me" in result["data"]:
                self._user = result["data"]["me"]
        except Exception:
            pass
    
    def register(self, email, password, first_name, last_name, role="PARENT"):
        """Register a new user account"""
        register_mutation = """
        mutation SignUp(
            $email: String!, 
            $password: String!, 
            $firstName: String!, 
            $lastName: String!,
            $role: String
        ) {
            createUser(
                email: $email, 
                password: $password, 
                firstName: $firstName, 
                lastName: $lastName,
                role: $role
            ) {
                user {
                    id
                    email
                }
            }
        }
        """
        
        variables = {
            "email": email,
            "password": password,
            "firstName": first_name,
            "lastName": last_name,
            "role": role
        }
        
        headers = {'Content-Type': 'application/json'} # Registration should not send auth token

        print("--- Attempting Registration ---")
        print(f"API URL: {API_URL}")
        # print(f"Mutation: {register_mutation}") # Can be verbose
        print(f"Variables: {json.dumps(variables, indent=2)}")
        print(f"Headers: {headers}")

        try:
            result = self.client.execute(
                query=register_mutation,
                variables=variables,
                headers=headers
            )
            print(f"Registration API Response: {json.dumps(result, indent=2)}")

            if result and "errors" in result:
                graphql_error = result["errors"][0]["message"]
                print(f"GraphQL Error during registration: {graphql_error}")
                return False, graphql_error
            
            user_data = result.get("data", {}).get("createUser", {}).get("user", {})
            if user_data and "id" in user_data:
                return True, "Registration successful"
            else:
                # This case implies data was returned but didn't contain the expected user ID.
                # It could be a successful call but unexpected response structure, or createUser resolved to null.
                print("Registration call successful, but user data not found in response or 'id' missing.")
                return False, "Registration failed: User data not found in response."

        except Exception as e:
                print(f"Network/Client Exception during registration: {type(e).__name__} - {str(e)}")
                return False, f"Registration error: An unexpected error occurred. {str(e)}"
    
    def logout(self):
        """Log the user out by removing the token"""
        self._clear_token()
    
    def is_authenticated(self):
        """Check if the user is authenticated"""
        return self._token is not None
    
    def get_token(self):
        """Get the current auth token"""
        return self._token
    
    def get_user(self):
        """Get the current user information"""
        return self._user
    
    def get_headers(self):
        """Get the authorization headers for API requests"""
        if self._token:
            return {"Authorization": f"JWT {self._token}"}
        return {}
