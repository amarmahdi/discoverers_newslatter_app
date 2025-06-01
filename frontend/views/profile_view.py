import flet as ft
from flet import (
    Column, Container, Card, Row, Text, 
    MainAxisAlignment, ProgressRing, 
    padding, TextField, ElevatedButton,
    Switch, Divider
)
from api.graphql_client import ApiClient


class ProfileView(Container):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.auth_service = app_instance.auth_service
        self.api_client = ApiClient(self.auth_service)
        self.expand = True
        self.padding = padding.only(left=20, right=20, top=20, bottom=80)
        
        # Data loading indicator
        self.loading = ProgressRing(width=24, height=24, stroke_width=2)
        
        # Selected tab index for profile sections
        self.selected_tab_index = 0
        
        # Button style for tab buttons
        button_style = ft.ButtonStyle(
            color={"selected": "#FFFFFF", "":""},
            bgcolor={"selected": "#2196F3", "":""},
            padding=10,
        )
        
        # Create profile section buttons instead of tabs
        self.profile_buttons = Row(
            controls=[
                ElevatedButton(
                    text="Profile",
                    icon="person_outline",
                    style=button_style,
                    data=0,  # Use data to track tab index
                    on_click=self.tab_button_clicked,
                    bgcolor="#2196F3" if self.selected_tab_index == 0 else "#BBDEFB",
                    color="#FFFFFF" if self.selected_tab_index == 0 else "#0D47A1",
                ),
                ElevatedButton(
                    text="Children",
                    icon="child_care",
                    style=button_style,
                    data=1,
                    on_click=self.tab_button_clicked,
                    bgcolor="#2196F3" if self.selected_tab_index == 1 else "#BBDEFB",
                    color="#FFFFFF" if self.selected_tab_index == 1 else "#0D47A1",
                ),
                ElevatedButton(
                    text="Subscriptions",
                    icon="notifications_outlined",
                    style=button_style,
                    data=2,
                    on_click=self.tab_button_clicked,
                    bgcolor="#2196F3" if self.selected_tab_index == 2 else "#BBDEFB",
                    color="#FFFFFF" if self.selected_tab_index == 2 else "#0D47A1",
                ),
            ],
            spacing=10,
        )
        
        # Container for tab content
        self.tab_content = Container(
            content=self.build_profile_content(),
            padding=padding.only(top=20),
            expand=True,
        )
        
        # Build the UI
        self.content = Column(
            [
                # Profile header
                Container(
                    content=Row(
                        [
                            Text(
                                "My Profile",
                                size=24, 
                                weight="bold",
                                color="#37474F",  # BLUE_GREY_800
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    margin=ft.margin.only(bottom=20),
                ),
                
                # Profile tabs
                self.profile_buttons,
                
                # Tab content area
                self.tab_content,
            ],
            spacing=16,
            expand=True,
        )
        
    def tab_button_clicked(self, e):
        # Set selected tab index based on button data
        self.selected_tab_index = e.control.data
        
        # Update button colors based on selection
        for button in self.profile_buttons.controls:
            if button.data == self.selected_tab_index:
                button.bgcolor = "#2196F3"
                button.color = "#FFFFFF"
            else:
                button.bgcolor = "#BBDEFB"
                button.color = "#0D47A1"
        
        # Show the appropriate content based on tab index
        if self.selected_tab_index == 0:  # Profile tab
            self.tab_content.content = self.build_profile_content()
        elif self.selected_tab_index == 1:  # Children tab
            self.tab_content.content = self.build_children_content()
        elif self.selected_tab_index == 2:  # Subscriptions tab
            self.tab_content.content = self.build_subscription_content()
        
        # Update the UI
        if self.page:
            self.page.update()
    
    def build_profile_content(self):
        # Get current user info
        user = self.auth_service.get_user() or {}
        first_name = user.get("first_name", "")
        last_name = user.get("last_name", "")
        email = user.get("email", "")
        
        return Column(
            [
                # Profile info card
                Card(
                    content=Container(
                        content=Column(
                            [
                                Text("Personal Information", size=18, weight="bold"),
                                Divider(height=1, color="#ECEFF1"),  # BLUE_GREY_100
                                TextField(
                                    label="First Name",
                                    value=first_name,
                                    disabled=True,
                                ),
                                TextField(
                                    label="Last Name",
                                    value=last_name,
                                    disabled=True,
                                ),
                                TextField(
                                    label="Email",
                                    value=email,
                                    disabled=True,
                                ),
                            ],
                            spacing=15,
                        ),
                        padding=15,
                    ),
                ),
                
                # Settings card
                Card(
                    content=Container(
                        content=Column(
                            [
                                Text("Account Settings", size=18, weight="bold"),
                                Divider(height=1, color="#ECEFF1"),  # BLUE_GREY_100
                                Row(
                                    [
                                        Text("Enable email notifications"),
                                        Switch(value=True),
                                    ],
                                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                Row(
                                    [
                                        Text("Receive newsletter updates"),
                                        Switch(value=True),
                                    ],
                                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                                ),
                            ],
                            spacing=15,
                        ),
                        padding=15,
                    ),
                    margin=ft.margin.only(top=10),
                ),
            ],
            spacing=10,
        )
    
    def build_children_content(self):
        return Column(
            [
                Card(
                    content=Container(
                        content=Column(
                            [
                                Row(
                                    [
                                        Text("My Children", size=18, weight="bold"),
                                        ElevatedButton(
                                            text="Add Child",
                                            icon="add",
                                        ),
                                    ],
                                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                Divider(height=1, color="#ECEFF1"),  # BLUE_GREY_100
                                Container(
                                    content=Text("No children added yet."),
                                    padding=padding.only(top=20, bottom=20),
                                    alignment=ft.alignment.center,
                                ),
                            ],
                            spacing=15,
                        ),
                        padding=15,
                    ),
                ),
            ],
        )
    
    def build_subscription_content(self):
        return Column(
            [
                Card(
                    content=Container(
                        content=Column(
                            [
                                Text("Notification Preferences", size=18, weight="bold"),
                                Divider(height=1, color="#ECEFF1"),  # BLUE_GREY_100
                                Row(
                                    [
                                        Text("Newsletters"),
                                        Switch(value=True),
                                    ],
                                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                Row(
                                    [
                                        Text("Announcements"),
                                        Switch(value=True),
                                    ],
                                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                Row(
                                    [
                                        Text("Events"),
                                        Switch(value=True),
                                    ],
                                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                                ),
                            ],
                            spacing=15,
                        ),
                        padding=15,
                    ),
                ),
            ],
        )
