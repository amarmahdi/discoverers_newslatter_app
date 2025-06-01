import flet as ft
from flet import (
    Column, Container, Card, Row, Text, 
    MainAxisAlignment, CrossAxisAlignment, ProgressRing, 
    padding, Icon, Image
)
import asyncio
from api.graphql_client import ApiClient
from datetime import datetime


class EventListView(Container):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.auth_service = app_instance.auth_service
        self.api_client = ApiClient(self.auth_service)
        self.expand = True
        self.padding = padding.only(left=20, right=20, top=20, bottom=80)
        
        # Data loading indicator
        self.loading = ProgressRing(width=24, height=24, stroke_width=2)
        
        # Events list container
        self.events_column = Column(spacing=15)
        
        # Initial loading message
        self.events_column.controls.append(
            Container(
                content=Row(
                    [
                        self.loading,
                        Text("Loading events...", size=14),
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
                            "Daycare Events",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_900,
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                
                # Events list
                self.events_column,
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Load events on initialization
        self.did_mount_async()
    
    def did_mount_async(self):
        """Load data asynchronously when the view is mounted"""
        # Create event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.create_task(self.load_events())
    
    async def load_events(self):
        """Load events from the API"""
        # Fetch events
        events, error = await self.api_client.get_events()
        
        # Clear loading indicator
        self.events_column.controls.clear()
        
        if events:
            # Sort events by start date
            try:
                events.sort(key=lambda x: x.get("startDate", ""), reverse=False)
            except Exception:
                pass
            
            # Group events by upcoming and past
            now = datetime.now()
            upcoming_events = []
            past_events = []
            
            for event in events:
                start_date = event.get("startDate", "")
                if start_date:
                    try:
                        start_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                        if start_obj > now:
                            upcoming_events.append(event)
                        else:
                            past_events.append(event)
                    except Exception:
                        upcoming_events.append(event)
                else:
                    upcoming_events.append(event)
            
            # Add upcoming events first
            if upcoming_events:
                self.events_column.controls.append(
                    Text(
                        "Upcoming Events",
                        size=18,
                        weight=ft.FontWeight.W500,
                        color=ft.Colors.BLUE_700,
                    )
                )
                
                for event in upcoming_events:
                    self.events_column.controls.append(
                        self.create_event_card(event)
                    )
            
            # Add past events
            if past_events:
                self.events_column.controls.append(
                    Container(
                        content=Text(
                            "Past Events",
                            size=18,
                            weight=ft.FontWeight.W500,
                            color=ft.Colors.BLUE_GREY_700,
                        ),
                        margin=ft.margin.only(top=20),
                    )
                )
                
                for event in past_events:
                    self.events_column.controls.append(
                        self.create_event_card(event, is_past=True)
                    )
            
            # If no events
            if not upcoming_events and not past_events:
                self.events_column.controls.append(
                    Container(
                        content=Text(
                            "No events found",
                            size=16,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(top=40),
                    )
                )
        else:
            self.events_column.controls.append(
                Container(
                    content=Text(
                        error or "Unable to load events",
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.RED_400,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=40),
                )
            )
        
        self.update()
    
    def create_event_card(self, event, is_past=False):
        """Create a card for an event"""
        title = event.get("title", "Untitled")
        description = event.get("description", "")
        location = event.get("location", "")
        start_date = event.get("startDate", "")
        end_date = event.get("endDate", "")
        created_by = event.get("createdBy", {})
        categories = event.get("categories", [])
        image = event.get("image", "")
        
        # Format date if available
        date_text = ""
        time_text = ""
        if start_date:
            try:
                from datetime import datetime
                start_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                date_text = start_obj.strftime("%B %d, %Y")
                time_text = start_obj.strftime("%I:%M %p")
                
                if end_date:
                    end_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    if start_obj.date() != end_obj.date():
                        date_text += f" - {end_obj.strftime('%B %d, %Y')}"
                    time_text += f" - {end_obj.strftime('%I:%M %p')}"
            except Exception:
                date_text = start_date
        
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
                        # Event image if available
                        Image(
                            src=image,
                            fit=ft.ImageFit.COVER,
                            width=400,
                            height=150,
                            border_radius=ft.border_radius.only(
                                top_left=8,
                                top_right=8,
                            ),
                        ) if image else Container(height=0),
                        
                        Container(
                            content=Column(
                                [
                                    # Date and time info
                                    Row(
                                        [
                                            Row(
                                                [
                                                    Icon(
                                                        name=ft.Icons.CALENDAR_TODAY,
                                                        size=14,
                                                        color=ft.Colors.BLUE_GREY_600,
                                                    ),
                                                    Text(
                                                        date_text,
                                                        size=14,
                                                        color=ft.Colors.BLUE_GREY_600,
                                                    ),
                                                ],
                                                spacing=5,
                                            ),
                                            Container(
                                                content=Text(
                                                    "PAST",
                                                    size=12,
                                                    color=ft.Colors.WHITE,
                                                    weight=ft.FontWeight.W500,
                                                ),
                                                bgcolor=ft.Colors.BLUE_GREY_500,
                                                border_radius=ft.border_radius.all(4),
                                                padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                                visible=is_past,
                                            ),
                                        ],
                                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                                    ) if date_text else Container(height=0),
                                    
                                    Row(
                                        [
                                            Icon(
                                                name=ft.Icons.ACCESS_TIME,
                                                size=14,
                                                color=ft.Colors.BLUE_GREY_600,
                                            ),
                                            Text(
                                                time_text,
                                                size=14,
                                                color=ft.Colors.BLUE_GREY_600,
                                            ),
                                        ],
                                        spacing=5,
                                    ) if time_text else Container(height=0),
                                    
                                    # Title and location
                                    Container(height=10),
                                    Text(
                                        title,
                                        size=18,
                                        weight=ft.FontWeight.W500,
                                        color=ft.Colors.BLUE_900,
                                    ),
                                    Container(height=5),
                                    
                                    Row(
                                        [
                                            Icon(
                                                name=ft.Icons.LOCATION_ON,
                                                size=16,
                                                color=ft.Colors.BLUE_GREY_600,
                                            ),
                                            Text(
                                                location,
                                                size=14,
                                                color=ft.Colors.BLUE_GREY_600,
                                            ),
                                        ],
                                        spacing=5,
                                    ) if location else Container(height=0),
                                    
                                    # Description
                                    Container(height=10),
                                    Text(
                                        description,
                                        size=14,
                                        color=ft.Colors.BLUE_GREY_800,
                                    ),
                                    
                                    # Categories
                                    Container(height=5),
                                    category_row if categories else Container(height=0),
                                ],
                            ),
                            padding=ft.padding.all(15),
                        ),
                    ],
                    spacing=0,
                ),
                opacity=0.7 if is_past else 1.0,
            ),
            elevation=1 if is_past else 2,
            margin=ft.margin.only(bottom=15),
        )
