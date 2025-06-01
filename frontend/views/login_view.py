import flet as ft
from flet import (
    Column, Container, ElevatedButton, 
    Text, TextField, Row, ProgressRing,
    MainAxisAlignment, CrossAxisAlignment
)


class LoginView(Container):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.auth_service = app_instance.auth_service
        self.expand = True
        self.bgcolor = ft.Colors.BLUE_50
        
        # Create form fields
        self.email_field = TextField(
            label="Email",
            hint_text="your@email.com",
            border_color=ft.Colors.BLUE_400,
            icon=ft.Icons.EMAIL,
            autofocus=True,
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
        
        # Progress indicator for login process
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
                                    size=80,
                                    color=ft.Colors.BLUE_700,
                                ),
                                margin=ft.margin.only(bottom=10),
                            ),
                            Text(
                                "Discoverers Daycare",
                                size=30,
                                weight=ft.FontWeight.BOLD,
                                color=ft.Colors.BLUE_700,
                            ),
                            Text(
                                "Newsletter App",
                                size=20,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.BLUE_500,
                            ),
                        ],
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                    ),
                    margin=ft.margin.only(top=60, bottom=40),
                ),
                
                # Login form
                Container(
                    content=Column(
                        [
                            Text(
                                "Login to your account",
                                size=20,
                                weight=ft.FontWeight.W_500,
                                color=ft.Colors.BLUE_900,
                            ),
                            Container(height=20),
                            self.email_field,
                            Container(height=10),
                            self.password_field,
                            Container(height=5),
                            self.error_text,
                            Container(height=20),
                            Container(
                                content=Row(
                                    [
                                        ElevatedButton(
                                            content=Row(
                                                [
                                                    Text("Login", size=16),
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
                                            on_click=self.login_clicked,
                                        ),
                                    ],
                                    alignment=MainAxisAlignment.CENTER,
                                ),
                            ),
                            Container(
                                content=Row(
                                    [
                                        Text("Don't have an account?"),
                                        ft.TextButton(
                                            "Register",
                                            on_click=self.go_to_register,
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
        )
    
    def login_clicked(self, e):
        """Handle login button click"""
        email = self.email_field.value
        password = self.password_field.value
        
        # Basic validation
        if not email or not password:
            self.error_text.value = "Please enter both email and password"
            self.error_text.visible = True
            self.update()
            return
        
        # Show progress indicator
        self.progress.visible = True
        self.update()
        
        # Attempt login
        success, message = self.auth_service.login(email, password)
        
        # Hide progress indicator
        self.progress.visible = False
        
        if success:
            # Clear any error messages
            self.error_text.visible = False
            
            # Show success message and redirect to dashboard
            self.app.page.snack_bar = ft.SnackBar(
                content=Text("Login successful!"),
                action="OK",
            )
            self.app.page.snack_bar.open = True
            self.app.page.update()
            
            # Navigate to dashboard
            self.app.page.go("/dashboard")
        else:
            # Show error message
            self.error_text.value = message
            self.error_text.visible = True
            self.update()
    
    def go_to_register(self, e):
        """Navigate to registration page"""
        self.app.page.go("/register")
