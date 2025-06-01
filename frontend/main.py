import flet as ft
from flet import (
    AppBar, Container, ElevatedButton, IconButton, Page, Row, 
    SnackBar, Text, TextButton, TextField, Icon, Card, Column, 
    Tabs, Tab, MainAxisAlignment, CrossAxisAlignment, 
    Divider, Switch, Checkbox, ProgressRing, Dropdown, PopupMenuButton, 
    PopupMenuItem
)
import os
import asyncio
from auth.auth_service import AuthService
from views.login_view import LoginView
from views.register_view import RegisterView
from views.dashboard import DashboardView
from views.newsletter_view import NewsletterListView, NewsletterDetailView
from views.announcement_view import AnnouncementListView
from views.event_view import EventListView
from views.profile_view import ProfileView
from utils.theme import get_theme


class DaycareNewsletterApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.auth_service = AuthService()
        self.setup_page()
        self.current_view = None
        self.setup_routes()
        
    def setup_page(self):
        """Configure the app's appearance and global settings"""
        self.page.title = "Discoverers Daycare Newsletter"
        self.page.theme = get_theme()
        self.page.window_width = 400
        self.page.window_height = 850
        self.page.window_resizable = True
        self.page.window_maximizable = True
        self.page.theme_mode = ft.ThemeMode.LIGHT
        self.page.padding = 0
        self.page.on_route_change = self.route_change
        self.page.on_view_pop = self.view_pop
        
        # Create app bar with title and theme toggle
        self.page.appbar = AppBar(
            title=Text("Discoverers Daycare", size=20, weight="bold"),
            center_title=True,
            bgcolor=ft.Colors.BLUE_700,
            actions=[
                IconButton(
                    icon=ft.Icons.BRIGHTNESS_6_OUTLINED,
                    tooltip="Toggle brightness",
                    on_click=self.toggle_theme_mode
                ),
                IconButton(
                    icon=ft.Icons.LOGOUT,
                    tooltip="Logout",
                    on_click=self.logout
                ),
            ],
        )
        
        # Create a sidebar navigation rail instead of bottom navigation bar
        self.navigation_rail = ft.NavigationRail(
            selected_index=0,
            label_type=ft.NavigationRailLabelType.ALL,
            min_width=100,
            min_extended_width=200,
            extended=True,
            destinations=[
                ft.NavigationRailDestination(
                    icon=ft.Icons.HOME_OUTLINED,
                    selected_icon=ft.Icons.HOME,
                    label="Home",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.NEWSPAPER_OUTLINED,
                    selected_icon=ft.Icons.NEWSPAPER,
                    label="Newsletters",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.ANNOUNCEMENT_OUTLINED, 
                    selected_icon=ft.Icons.ANNOUNCEMENT,
                    label="Announcements",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.EVENT_OUTLINED,
                    selected_icon=ft.Icons.EVENT,
                    label="Events",
                ),
                ft.NavigationRailDestination(
                    icon=ft.Icons.PERSON_OUTLINED,
                    selected_icon=ft.Icons.PERSON,
                    label="Profile",
                ),
            ],
            on_change=self.navigation_change,
        )

    def setup_routes(self):
        """Set up routing for the application"""
        self.page.views.clear()
        self.page.views.append(
            ft.View(
                "/",
                [
                    LoginView(self)
                ],
                padding=0,
                bgcolor=ft.Colors.WHITE
            )
        )
        
    def navigation_change(self, e):
        """Handle navigation bar item selection"""
        index = e.control.selected_index
        if index == 0:
            self.page.go("/dashboard")
        elif index == 1:
            self.page.go("/newsletters")
        elif index == 2:
            self.page.go("/announcements")
        elif index == 3:
            self.page.go("/events")
        elif index == 4:
            self.page.go("/profile")
            
    def route_change(self, route):
        """Handle route changes and display appropriate views"""
        self.page.views.clear()
        
        # Check if user is authenticated for protected routes
        is_authenticated = self.auth_service.is_authenticated()
        
        route_path = route.route
        if route_path == "/":
            # Login is the default route
            self.page.views.append(
                ft.View(
                    "/",
                    [LoginView(self)],
                    padding=0,
                    bgcolor=ft.Colors.WHITE
                )
            )
        elif route_path == "/register":
            # Registration page
            self.page.views.append(
                ft.View(
                    "/register",
                    [RegisterView(self)],
                    padding=0,
                    bgcolor=ft.Colors.WHITE
                )
            )
        elif route_path == "/dashboard":
            # Main dashboard
            if not is_authenticated:
                self.page.go("/")  # Redirect to login
                return
                
            # Update the selected tab in the navigation rail
            self.navigation_rail.selected_index = 0
            
            # Create a row with navigation rail on the left and content on the right
            self.page.views.append(
                ft.View(
                    "/dashboard",
                    [
                        ft.Row(
                            [
                                # Left side - Navigation rail
                                self.navigation_rail,
                                # Right side - Content area
                                ft.VerticalDivider(width=1),
                                DashboardView(self),
                            ],
                            expand=True,
                        )
                    ],
                    padding=0,
                    bgcolor=ft.Colors.WHITE
                )
            )
        elif route_path == "/newsletters":
            # Newsletters page
            if not is_authenticated:
                self.page.go("/")  # Redirect to login
                return
                
            # Update the selected tab in the navigation rail
            self.navigation_rail.selected_index = 1
            
            # Create a row with navigation rail on the left and content on the right
            self.page.views.append(
                ft.View(
                    "/newsletters",
                    [
                        ft.Row(
                            [
                                # Left side - Navigation rail
                                self.navigation_rail,
                                # Right side - Content area
                                ft.VerticalDivider(width=1),
                                NewsletterListView(self),
                            ],
                            expand=True,
                        )
                    ],
                    padding=0,
                    bgcolor=ft.Colors.WHITE
                )
            )
        elif route_path.startswith("/newsletter/"):
            # Newsletter detail page
            if not is_authenticated:
                self.page.go("/")  # Redirect to login
                return
                
            # Keep the same selected index as the newsletters page
            self.navigation_rail.selected_index = 1
            
            newsletter_id = route_path.split("/")[-1]
            self.page.views.append(
                ft.View(
                    route_path,
                    [
                        ft.Row(
                            [
                                # Left side - Navigation rail
                                self.navigation_rail,
                                # Right side - Content area
                                ft.VerticalDivider(width=1),
                                NewsletterDetailView(self, newsletter_id),
                            ],
                            expand=True,
                        )
                    ],
                    padding=0,
                    bgcolor=ft.Colors.WHITE
                )
            )
        elif route_path == "/announcements":
            # Announcements page
            if not is_authenticated:
                self.page.go("/")  # Redirect to login
                return
                
            # Update the selected tab in the navigation rail
            self.navigation_rail.selected_index = 2
            
            self.page.views.append(
                ft.View(
                    "/announcements",
                    [
                        ft.Row(
                            [
                                # Left side - Navigation rail
                                self.navigation_rail,
                                # Right side - Content area
                                ft.VerticalDivider(width=1),
                                AnnouncementListView(self),
                            ],
                            expand=True,
                        )
                    ],
                    padding=0,
                    bgcolor=ft.Colors.WHITE
                )
            )
        elif route_path == "/events":
            # Events page
            if not is_authenticated:
                self.page.go("/")  # Redirect to login
                return
                
            # Update the selected tab in the navigation rail
            self.navigation_rail.selected_index = 3
            
            self.page.views.append(
                ft.View(
                    "/events",
                    [
                        ft.Row(
                            [
                                # Left side - Navigation rail
                                self.navigation_rail,
                                # Right side - Content area
                                ft.VerticalDivider(width=1),
                                EventListView(self),
                            ],
                            expand=True,
                        )
                    ],
                    padding=0,
                    bgcolor=ft.Colors.WHITE
                )
            )
        elif route_path == "/profile":
            # Profile page
            if not is_authenticated:
                self.page.go("/")  # Redirect to login
                return
                
            # Update the selected tab in the navigation rail
            self.navigation_rail.selected_index = 4
            
            self.page.views.append(
                ft.View(
                    "/profile",
                    [
                        ft.Row(
                            [
                                # Left side - Navigation rail
                                self.navigation_rail,
                                # Right side - Content area
                                ft.VerticalDivider(width=1),
                                ProfileView(self),
                            ],
                            expand=True,
                        )
                    ],
                    padding=0,
                    bgcolor=ft.Colors.WHITE
                )
            )
        self.page.update()
        
    def view_pop(self, view):
        """Handle the back button navigation"""
        self.page.views.pop()
        top_view = self.page.views[-1]
        self.page.go(top_view.route)
        
    def toggle_theme_mode(self, e):
        """Toggle between light and dark theme"""
        self.page.theme_mode = (
            ft.ThemeMode.DARK
            if self.page.theme_mode == ft.ThemeMode.LIGHT
            else ft.ThemeMode.LIGHT
        )
        self.page.update()
        
    def logout(self, e=None):
        """Log the user out and redirect to login page"""
        self.auth_service.logout()
        self.page.snack_bar = SnackBar(
            content=Text("You have been logged out"),
            action="OK",
        )
        self.page.snack_bar.open = True
        self.page.navigation_bar.visible = False
        self.page.go("/")
        self.page.update()


def main(page: ft.Page):
    """Main entry point for the application"""
    app = DaycareNewsletterApp(page)
    page.go(page.route)


# Run the app
ft.app(target=main)
