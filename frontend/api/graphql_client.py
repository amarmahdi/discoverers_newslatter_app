import aiohttp
from typing import Any, Dict, Optional, Tuple

# GraphQL API endpoint
API_URL = "http://localhost:8000/graphql/"

class ApiClient:
    """Client for interacting with the GraphQL API"""
    
    def __init__(self, auth_service=None):
        self.auth_service = auth_service
    
    def _get_headers(self):
        """Get headers with authentication token if available"""
        if self.auth_service and self.auth_service.is_authenticated():
            return self.auth_service.get_headers()
        return {}
    
    async def _execute_query(self, query: str, variables: Optional[Dict] = None) -> Tuple[Any, Optional[str]]:
        """Execute a GraphQL query asynchronously"""
        if variables is None:
            variables = {}
            
        headers = self._get_headers()
        headers["Content-Type"] = "application/json"
        
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    API_URL,
                    json={"query": query, "variables": variables},
                    headers=headers
                ) as response:
                    result = await response.json()
                    
                    if "errors" in result:
                        return None, result["errors"][0]["message"]
                        
                    return result.get("data"), None
                    
            except Exception as e:
                return None, str(e)
    
    async def get_newsletters(self, status=None):
        """Fetch newsletters from the API"""
        query = """
        query GetNewsletters($status: String) {
            newsletters(status: $status) {
                id
                title
                subtitle
                content
                createdAt
                publishedAt
                featured
                createdBy {
                    email
                    firstName
                    lastName
                }
                categories {
                    id
                    name
                }
                coverImage
            }
        }
        """
        
        variables = {}
        if status:
            variables["status"] = status
            
        data, error = await self._execute_query(query, variables)
        return data.get("newsletters", []) if data else [], error
    
    async def get_newsletter_detail(self, newsletter_id):
        """Fetch a specific newsletter by ID"""
        query = """
        query GetNewsletter($id: ID!) {
            newsletter(id: $id) {
                id
                title
                subtitle
                content
                createdAt
                publishedAt
                featured
                createdBy {
                    email
                    firstName
                    lastName
                }
                categories {
                    id
                    name
                }
                coverImage
                events {
                    id
                    title
                    description
                    startDate
                    endDate
                    location
                }
            }
        }
        """
        
        data, error = await self._execute_query(query, {"id": newsletter_id})
        return (data.get("newsletter"), error) if data else (None, error or "No data returned")
    
    async def get_announcements(self, is_active=True):
        """Fetch announcements from the API"""
        query = """
        query GetAnnouncements($isActive: Boolean) {
            announcements(isActive: $isActive) {
                id
                title
                content
                priority
                isActive
                createdAt
                expiryDate
                createdBy {
                    id
                    firstName
                    lastName
                }
                categories {
                    id
                    name
                }
            }
        }
        """
        
        data, error = await self._execute_query(query, {"isActive": is_active})
        return (data.get("announcements", []), error) if data else ([], error or "No data returned")
    
    async def get_events(self, is_active=True):
        """Fetch events from the API"""
        query = """
        query GetEvents($isActive: Boolean) {
            events(isActive: $isActive) {
                id
                title
                description
                startDate
                endDate
                location
                createdBy {
                    email
                    firstName
                    lastName
                }
                categories {
                    id
                    name
                }
                image
            }
        }
        """
        
        data, error = await self._execute_query(query, {"isActive": is_active})
        return (data.get("events", []), error) if data else ([], error or "No data returned")
    
    async def create_announcement(self, title, content, priority="MEDIUM", expiry_date=None, category_ids=None):
        """Create a new announcement"""
        mutation = """
        mutation createAnnouncement($title: String!, $content: String!, $priority: String, $expiryDate: DateTime, $categoryIds: [ID]) {
            createAnnouncement(
                title: $title,
                content: $content,
                priority: $priority,
                expiryDate: $expiryDate,
                categoryIds: $categoryIds
            ) {
                announcement {
                    id
                    title
                    content
                    priority
                    expiryDate
                    createdAt
                    createdBy {
                        id
                        firstName
                        lastName
                    }
                }
            }
        }
        """
        
        variables = {
            "title": title,
            "content": content,
            "priority": priority,
            "expiryDate": expiry_date,
            "categoryIds": category_ids or []
        }
            
        data, error = await self._execute_query(mutation, variables)
        if error:
            return None, error
            
        return data.get("createAnnouncement", {}).get("announcement"), None
    
    async def get_upcoming_events(self):
        """Fetch upcoming events from the API"""
        query = """
        query {
            upcomingEvents {
                id
                title
                description
                startDate
                endDate
                location
                createdBy {
                    email
                    firstName
                    lastName
                }
                categories {
                    id
                    name
                }
                image
            }
        }
        """
        
        data, error = await self._execute_query(query, {})
        return (data.get("upcomingEvents", []), error) if data else ([], error or "No data returned")
    
    async def get_user_profile(self):
        """Fetch the current user's profile"""
        query = """
        query {
            me {
                id
                email
                firstName
                lastName
                role
                phoneNumber
                address
                childrenInfo
                emergencyContact
                position
                bio
                children {
                    id
                    firstName
                    lastName
                    dateOfBirth
                    allergies
                    medicalNotes
                    group
                }
            }
        }
        """
        
        data, error = await self._execute_query(query, {})
        return (data.get("me"), error) if data else (None, error or "No data returned")
    
    async def get_subscription_status(self):
        """Fetch the user's newsletter subscription status"""
        query = """
        query {
            mySubscription {
                isSubscribed
                groups {
                    id
                    name
                    description
                }
            }
        }
        """
        
        data, error = await self._execute_query(query, {})
        return (data.get("mySubscription"), error) if data else (None, error or "No data returned")
    
    async def update_subscription(self, is_subscribed, group_ids=None):
        """Update the user's newsletter subscription preferences"""
        mutation = """
        mutation UpdateSubscription($isSubscribed: Boolean!, $groupIds: [ID]) {
            updateSubscription(isSubscribed: $isSubscribed, groupIds: $groupIds) {
                subscription {
                    isSubscribed
                    groups {
                        id
                        name
                    }
                }
            }
        }
        """
        
        variables = {
            "isSubscribed": is_subscribed,
            "groupIds": group_ids or []
        }
        
        data, error = await self._execute_query(mutation, variables)
        if error:
            return None, error
            
        return data.get("updateSubscription", {}).get("subscription"), None
