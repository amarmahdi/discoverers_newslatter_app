import flet as ft
from flet import (
    Column, Container, Card, Row, Text, 
    MainAxisAlignment, CrossAxisAlignment, ProgressRing, 
    padding, Icon
)
import asyncio
from api.graphql_client import ApiClient


class AnnouncementListView(Container):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.auth_service = app_instance.auth_service
        self.api_client = ApiClient(self.auth_service)
        self.expand = True
        self.padding = padding.only(left=20, right=20, top=20, bottom=80)
        
        # Data loading indicator
        self.loading = ProgressRing(width=24, height=24, stroke_width=2)
        
        # Announcements list container
        self.announcements_column = Column(spacing=15)
        
        # Initial loading message
        self.announcements_column.controls.append(
            Container(
                content=Row(
                    [
                        self.loading,
                        Text("Loading announcements...", size=14),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                alignment=ft.alignment.center,
                margin=ft.margin.only(top=20),
            )
        )
        
        # Build the UI
        self.content = Column(
            [
                # Page header
                Row(
                    [
                        Text(
                            "Announcements",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_900,
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                
                # Announcement list
                self.announcements_column,
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Load announcements on initialization
        self.did_mount_async()
    
    def did_mount_async(self):
        """Load data asynchronously when the view is mounted"""
        # Create event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.create_task(self.load_announcements())
    
    async def load_announcements(self):
        """Load announcements from the API"""
        # Fetch announcements
        announcements, error = await self.api_client.get_announcements()
        
        # Clear loading indicator
        self.announcements_column.controls.clear()
        
        if announcements:
            if announcements:
                # Group announcements by priority
                urgent = [a for a in announcements if a.get("priority") == "URGENT"]
                high = [a for a in announcements if a.get("priority") == "HIGH"]
                medium = [a for a in announcements if a.get("priority") == "MEDIUM"]
                low = [a for a in announcements if a.get("priority") == "LOW"]
                
                # Add urgent announcements first
                if urgent:
                    self.announcements_column.controls.append(
                        Text(
                            "Urgent Announcements",
                            size=18,
                            weight=ft.FontWeight.W500,
                            color=ft.Colors.RED_700,
                        )
                    )
                    
                    for announcement in urgent:
                        self.announcements_column.controls.append(
                            self.create_announcement_card(announcement)
                        )
                
                # Add high priority announcements
                if high:
                    self.announcements_column.controls.append(
                        Text(
                            "Important Announcements",
                            size=18,
                            weight=ft.FontWeight.W500,
                            color=ft.Colors.ORANGE_800,
                        )
                    )
                    
                    for announcement in high:
                        self.announcements_column.controls.append(
                            self.create_announcement_card(announcement)
                        )
                
                # Add medium priority announcements
                if medium:
                    self.announcements_column.controls.append(
                        Text(
                            "General Announcements",
                            size=18,
                            weight=ft.FontWeight.W500,
                            color=ft.Colors.BLUE_700,
                        )
                    )
                    
                    for announcement in medium:
                        self.announcements_column.controls.append(
                            self.create_announcement_card(announcement)
                        )
                
                # Add low priority announcements
                if low:
                    self.announcements_column.controls.append(
                        Text(
                            "Other Announcements",
                            size=18,
                            weight=ft.FontWeight.W500,
                            color=ft.Colors.GREEN_700,
                        )
                    )
                    
                    for announcement in low:
                        self.announcements_column.controls.append(
                            self.create_announcement_card(announcement)
                        )
            else:
                self.announcements_column.controls.append(
                    Container(
                        content=Text(
                            "No announcements found",
                            size=16,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(top=40),
                    )
                )
        else:
            self.announcements_column.controls.append(
                Container(
                    content=Text(
                        error or "Unable to load announcements",
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.RED_400,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=40),
                )
            )
        
        self.update()
    
    def create_announcement_card(self, announcement):
        """Create a card for an announcement"""
        title = announcement.get("title", "Untitled")
        content = announcement.get("content", "")
        priority = announcement.get("priority", "MEDIUM")
        created_at = announcement.get("createdAt", "")
        expiry_date = announcement.get("expiryDate")
        created_by = announcement.get("createdBy", {})
        categories = announcement.get("categories", [])
        image = announcement.get("image", "")
        
        # Determine color based on priority
        priority_colors = {
            "LOW": ft.Colors.GREEN,
            "MEDIUM": ft.Colors.BLUE,
            "HIGH": ft.Colors.ORANGE,
            "URGENT": ft.Colors.RED,
        }
        priority_color = priority_colors.get(priority, ft.Colors.BLUE)
        
        # Format date if available
        date_text = ""
        if created_at:
            try:
                from datetime import datetime
                date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                date_text = date_obj.strftime("%B %d, %Y")
            except Exception:
                date_text = created_at
        
        # Format expiry date if available
        expiry_text = ""
        if expiry_date:
            try:
                from datetime import datetime
                date_obj = datetime.fromisoformat(expiry_date.replace('Z', '+00:00'))
                expiry_text = f"Expires: {date_obj.strftime('%B %d, %Y')}"
            except Exception:
                expiry_text = f"Expires: {expiry_date}"
        
        # Author information
        author_name = f"{created_by.get('firstName', '')} {created_by.get('lastName', '')}".strip()
        if not author_name:
            author_name = created_by.get('email', 'Unknown')
        
        # Category tags
        category_row = Row(
            controls=[
                Container(
                    content=Text(
                        category.get("name", ""),
                        size=12,
                        color=ft.Colors.WHITE,
                    ),
                    bgcolor=ft.Colors.BLUE_400,
                    border_radius=ft.border_radius.all(4),
                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                    margin=ft.margin.only(right=5, top=5),
                )
                for category in categories[:3]  # Limit to 3 categories
            ],
            wrap=True,
            spacing=0,
        )
        
        return Card(
            content=Container(
                content=Column(
                    [
                        # Header with priority badge
                        Row(
                            [
                                Container(
                                    content=Text(
                                        priority,
                                        size=12,
                                        color=ft.Colors.WHITE,
                                        weight=ft.FontWeight.W500,
                                    ),
                                    bgcolor=priority_color,
                                    border_radius=ft.border_radius.all(4),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                ),
                                Text(
                                    date_text,
                                    size=12,
                                    color=ft.Colors.BLUE_GREY_500,
                                ),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        
                        # Title and content
                        Container(height=10),
                        Text(
                            title,
                            size=18,
                            weight=ft.FontWeight.W500,
                            color=ft.Colors.BLUE_900,
                        ),
                        Container(height=5),
                        Text(
                            content,
                            size=14,
                            color=ft.Colors.BLUE_GREY_800,
                        ),
                        
                        # Categories
                        Container(height=5),
                        category_row if categories else Container(height=0),
                        
                        # Footer with author and expiry info
                        Container(height=10),
                        Row(
                            [
                                Row(
                                    [
                                        Icon(
                                            name=ft.Icons.PERSON,
                                            size=14,
                                            color=ft.Colors.BLUE_GREY_600,
                                        ),
                                        Text(
                                            author_name,
                                            size=12,
                                            color=ft.Colors.BLUE_GREY_600,
                                        ),
                                    ],
                                    spacing=5,
                                ),
                                Text(
                                    expiry_text,
                                    size=12,
                                    color=ft.Colors.BLUE_GREY_600,
                                    italic=True,
                                ) if expiry_text else Container(width=0),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                        ),
                    ],
                ),
                padding=ft.padding.all(15),
                border=ft.border.all(
                    width=2, 
                    color=priority_color if priority in ["URGENT", "HIGH"] else ft.Colors.TRANSPARENT
                ),
                border_radius=ft.border_radius.all(8),
            ),
            elevation=2 if priority in ["URGENT", "HIGH"] else 1,
            margin=ft.margin.only(bottom=15),
        )
