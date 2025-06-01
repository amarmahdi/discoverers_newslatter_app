import flet as ft
from flet import (
    Column, Container, ElevatedButton, 
    Text, TextField, Row, ProgressRing,
    MainAxisAlignment, CrossAxisAlignment,
    Dropdown, dropdown
)


class RegisterView(Container):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.auth_service = app_instance.auth_service
        self.expand = True
        self.bgcolor = ft.Colors.BLUE_50
        
        # Create form fields
        self.first_name_field = TextField(
            label="First Name",
            border_color=ft.Colors.BLUE_400,
            icon=ft.Icons.PERSON,
            autofocus=True,
            height=50,
            text_size=16,
            width=320,
        )
        
        self.last_name_field = TextField(
            label="Last Name",
            border_color=ft.Colors.BLUE_400,
            icon=ft.Icons.PERSON_OUTLINE,
            height=50,
            text_size=16,
            width=320,
        )
        
        self.email_field = TextField(
            label="Email",
            hint_text="your@email.com",
            border_color=ft.Colors.BLUE_400,
            icon=ft.Icons.EMAIL,
            height=50,
            text_size=16,
            width=320,
            keyboard_type=ft.KeyboardType.EMAIL,
        )
        
        self.password_field = TextField(
            label="Password",
            password=True,
            can_reveal_password=True,
            border_color=ft.Colors.BLUE_400,
            icon=ft.Icons.LOCK,
            height=50,
            text_size=16,
            width=320,
        )
        
        self.confirm_password_field = TextField(
            label="Confirm Password",
            password=True,
            can_reveal_password=True,
            border_color=ft.Colors.BLUE_400,
            icon=ft.Icons.LOCK_OUTLINE,
            height=50,
            text_size=16,
            width=320,
        )
        
        self.role_dropdown = Dropdown(
            label="Role",
            hint_text="Select your role",
            border_color=ft.Colors.BLUE_400,
            options=[
                dropdown.Option("PARENT", "Parent"),
                dropdown.Option("STAFF", "Staff"),
            ],
            width=320,
            value="PARENT",
        )
        
        # Progress indicator for registration process
        self.progress = ProgressRing(
            width=20, 
            height=20, 
            stroke_width=2,
            visible=False
        )
        
        # Error message display
        self.error_text = Text(
            value="",
            color=ft.Colors.RED_600,
            size=14,
            visible=False
        )
        
        # Build the UI
        self.content = Column(
            [
                # Logo and app name
                Container(
                    content=Column(
                        [
                            Container(
                                content=ft.Icon(
                                    name=ft.Icons.CHILD_CARE,
                                    size=60,
                                    color=ft.Colors.BLUE_700,
                                ),
                                margin=ft.margin.only(bottom=10),
                            ),
                            Text(
                                "Create Account",
                                size=28,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700,
                            ),
                        ],
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                    ),
                    margin=ft.margin.only(top=40, bottom=20),
                ),
                
                # Registration form
                Container(
                    content=Column(
                        [
                            self.first_name_field,
                            Container(height=10),
                            self.last_name_field,
                            Container(height=10),
                            self.email_field,
                            Container(height=10),
                            self.password_field,
                            Container(height=10),
                            self.confirm_password_field,
                            Container(height=10),
                            self.role_dropdown,
                            Container(height=5),
                            self.error_text,
                            Container(height=20),
                            Container(
                                content=Row(
                                    [
                                        ElevatedButton(
                                            content=Row(
                                                [
                                                    Text("Register", size=16),
                                                    self.progress,
                                                ],
                                                spacing=10,
                                                alignment=MainAxisAlignment.CENTER,
                                            ),
                                            width=320,
                                            height=50,
                                            style=ft.ButtonStyle(
                                                bgcolor=ft.Colors.BLUE_700,
                                                color=ft.Colors.WHITE,
                                                shape={
                                                    "": ft.RoundedRectangleBorder(radius=8),
                                                },
                                                elevation={"": 1},
                                            ),
                                            on_click=self.register_clicked,
                                        ),
                                    ],
                                    alignment=MainAxisAlignment.CENTER,
                                ),
                            ),
                            Container(
                                content=Row(
                                    [
                                        Text("Already have an account?"),
                                        ft.TextButton(
                                            "Login",
                                            on_click=self.go_to_login,
                                        ),
                                    ],
                                    alignment=MainAxisAlignment.CENTER,
                                ),
                                margin=ft.margin.only(top=20),
                            ),
                        ],
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                        spacing=0,
                    ),
                    padding=ft.padding.all(20),
                    bgcolor=ft.Colors.WHITE,
                    border_radius=ft.border_radius.all(10),
                    width=360,
                ),
            ],
            alignment=MainAxisAlignment.START,
            horizontal_alignment=CrossAxisAlignment.CENTER,
            scroll=ft.ScrollMode.AUTO,
        )
    
    def register_clicked(self, e):
        """Handle registration button click"""
        first_name = self.first_name_field.value
        last_name = self.last_name_field.value
        email = self.email_field.value
        password = self.password_field.value
        confirm_password = self.confirm_password_field.value
        role = self.role_dropdown.value
        
        # Basic validation
        if not first_name or not last_name or not email or not password or not confirm_password:
            self.error_text.value = "Please fill in all fields"
            self.error_text.visible = True
            self.update()
            return
        
        if password != confirm_password:
            self.error_text.value = "Passwords do not match"
            self.error_text.visible = True
            self.update()
            return
        
        if len(password) < 8:
            self.error_text.value = "Password must be at least 8 characters"
            self.error_text.visible = True
            self.update()
            return
        
        # Show progress indicator
        self.progress.visible = True
        self.update()
        
        # Attempt registration
        success, message = self.auth_service.register(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role
        )
        
        # Hide progress indicator
        self.progress.visible = False
        
        if success:
            # Clear any error messages
            self.error_text.visible = False
            
            # Show success message and redirect to login
            self.app.page.snack_bar = ft.SnackBar(
                content=Text("Registration successful! Please login with your new account."),
                action="OK",
            )
            self.app.page.snack_bar.open = True
            self.app.page.update()
            
            # Navigate to login
            self.app.page.go("/")
        else:
            # Show error message
            self.error_text.value = message
            self.error_text.visible = True
            self.update()
    
    def go_to_login(self, e):
        """Navigate to login page"""
        self.app.page.go("/")
