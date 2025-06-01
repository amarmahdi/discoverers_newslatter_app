import flet as ft
from flet import (
    Column, Container, Card, Row, Text, 
    IconButton, Icon, MainAxisAlignment, 
    CrossAxisAlignment, ProgressRing, 
    ButtonStyle, RoundedRectangleBorder, padding,
    Tabs, Tab, Divider, Image, ElevatedButton
)
import asyncio
from api.graphql_client import ApiClient


class NewsletterListView(Container):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.auth_service = app_instance.auth_service
        self.api_client = ApiClient(self.auth_service)
        self.expand = True
        self.padding = padding.only(left=20, right=20, top=20, bottom=80)
        
        # Tabs for filtering newsletters
        self.tabs = Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                Tab(
                    text="All",
                    icon=ft.Icons.ALL_INBOX,
                ),
                Tab(
                    text="Featured",
                    icon=ft.Icons.STAR_OUTLINE,
                ),
            ],
            on_change=self.tab_changed
        )
        
        # Data loading indicator
        self.loading = ProgressRing(width=24, height=24, stroke_width=2)
        
        # Newsletter list container
        self.newsletters_column = Column(spacing=10)
        
        # Initial loading message
        self.newsletters_column.controls.append(
            Container(
                content=Row(
                    [
                        self.loading,
                        Text("Loading newsletters...", size=14),
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
                            "Newsletters",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_900,
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                
                # Filter tabs
                self.tabs,
                
                # Newsletter list
                self.newsletters_column,
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Load newsletters on initialization
        self.did_mount_async()
    
    def did_mount_async(self):
        """Load data asynchronously when the view is mounted"""
        # Create an event loop if one doesn't exist
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        # Run the coroutine in the event loop
        loop.create_task(self.load_newsletters())
    
    async def load_newsletters(self, filter_featured=False):
        """Load newsletters from the API"""
        # Clear previous newsletters
        self.newsletters_column.controls = [
            Container(
                content=Row(
                    [
                        self.loading,
                        Text("Loading newsletters...", size=14),
                    ],
                    alignment=MainAxisAlignment.CENTER,
                    spacing=10,
                ),
                alignment=ft.alignment.center,
                margin=ft.margin.only(top=20),
            )
        ]
        self.update()
        
        # Fetch newsletters
        newsletters, error = await self.api_client.get_newsletters()
        
        # Clear loading indicator
        self.newsletters_column.controls.clear()
        
        if newsletters:
            # Filter featured newsletters if requested
            if filter_featured:
                newsletters = [n for n in newsletters if n.get("featured", False)]
            
            if newsletters:
                # Create a card for each newsletter
                for newsletter in newsletters:
                    self.newsletters_column.controls.append(
                        self.create_newsletter_card(newsletter)
                    )
            else:
                self.newsletters_column.controls.append(
                    Container(
                        content=Text(
                            "No newsletters found",
                            size=16,
                            text_align=ft.TextAlign.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(top=40),
                    )
                )
        else:
            self.newsletters_column.controls.append(
                Container(
                    content=Text(
                        error or "Unable to load newsletters",
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.RED_400,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=40),
                )
            )
        
        self.update()
    
    def tab_changed(self, e):
        """Handle tab selection change"""
        selected_index = e.control.selected_index
        if selected_index == 0:  # All newsletters
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.create_task(self.load_newsletters(filter_featured=False))
        elif selected_index == 1:  # Featured newsletters
            # Create event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            loop.create_task(self.load_newsletters(filter_featured=True))
    
    def create_newsletter_card(self, newsletter):
        """Create a card for a newsletter"""
        title = newsletter.get("title", "Untitled")
        subtitle = newsletter.get("subtitle", "")
        content = newsletter.get("content", "")
        published_at = newsletter.get("publishedAt", "")
        created_by = newsletter.get("createdBy", {})
        categories = newsletter.get("categories", [])
        cover_image = newsletter.get("coverImage", "")
        
        # Format date if available
        date_text = ""
        if published_at:
            try:
                from datetime import datetime
                date_obj = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                date_text = date_obj.strftime("%B %d, %Y")
            except Exception:
                date_text = published_at
        
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
                    margin=ft.margin.only(right=5),
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
                        # Cover image if available
                        Image(
                            src=cover_image,
                            fit=ft.ImageFit.COVER,
                            width=400,
                            height=150,
                            border_radius=ft.border_radius.only(
                                top_left=8,
                                top_right=8,
                            ),
                        ) if cover_image else Container(height=0),
                        
                        Container(
                            content=Column(
                                [
                                    # Header with date and featured status
                                    Row(
                                        [
                                            Text(
                                                date_text,
                                                size=12,
                                                color=ft.Colors.BLUE_GREY_500,
                                            ),
                                            Icon(
                                                name=ft.Icons.STAR,
                                                color=ft.Colors.AMBER_400,
                                                size=20,
                                                visible=newsletter.get("featured", False),
                                            ),
                                        ],
                                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                    
                                    # Title and subtitle
                                    Container(height=5),
                                    Text(
                                        title,
                                        size=18,
                                        weight=ft.FontWeight.W500,
                                        color=ft.Colors.BLUE_900,
                                    ),
                                    Container(height=3),
                                    Text(
                                        subtitle,
                                        size=14,
                                        weight=ft.FontWeight.W400,
                                        color=ft.Colors.BLUE_GREY_700,
                                        visible=bool(subtitle),
                                    ),
                                    Container(height=5),
                                    
                                    # Preview of content
                                    Text(
                                        content[:150] + ("..." if len(content) > 150 else ""),
                                        size=14,
                                        color=ft.Colors.BLUE_GREY_800,
                                        max_lines=3,
                                        overflow=ft.TextOverflow.ELLIPSIS,
                                    ),
                                    Container(height=10),
                                    
                                    # Categories
                                    category_row if categories else Container(height=0),
                                    Container(height=10),
                                    
                                    # Author and read more button
                                    Row(
                                        [
                                            Text(
                                                f"By {author_name}",
                                                size=12,
                                                color=ft.Colors.BLUE_GREY_600,
                                                italic=True,
                                            ),
                                            ft.ElevatedButton(
                                                "Read More",
                                                style=ButtonStyle(
                                                    color={"": ft.Colors.WHITE},
                                                    bgcolor={"": ft.Colors.BLUE_700},
                                                    padding={"": 10},
                                                ),
                                                height=32,
                                                on_click=lambda e, id=newsletter.get("id"): self.open_newsletter(id),
                                            ),
                                        ],
                                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                                    ),
                                ],
                            ),
                            padding=ft.padding.all(15),
                        ),
                    ],
                    spacing=0,
                ),
            ),
            elevation=2,
            margin=ft.margin.only(bottom=15),
        )
    
    def open_newsletter(self, newsletter_id):
        """Open a specific newsletter"""
        if newsletter_id:
            self.app.page.go(f"/newsletter/{newsletter_id}")


class NewsletterDetailView(Container):
    def __init__(self, app_instance, newsletter_id):
        super().__init__()
        self.app = app_instance
        self.auth_service = app_instance.auth_service
        self.api_client = ApiClient(self.auth_service)
        self.newsletter_id = newsletter_id
        self.expand = True
        self.padding = padding.only(left=20, right=20, top=20, bottom=80)
        
        # Data loading indicator
        self.loading = ProgressRing(width=24, height=24, stroke_width=2)
        
        # Newsletter content container
        self.content_column = Column(spacing=10)
        
        # Initial loading message
        self.content_column.controls.append(
            Container(
                content=Row(
                    [
                        self.loading,
                        Text("Loading newsletter...", size=14),
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
                # Back button
                Row(
                    [
                        IconButton(
                            icon=ft.Icons.ARROW_BACK,
                            tooltip="Back to newsletters",
                            on_click=self.go_back,
                        ),
                    ],
                ),
                
                # Newsletter content
                self.content_column,
            ],
            spacing=10,
            scroll=ft.ScrollMode.AUTO,
        )
        
        # Load newsletter on initialization
        self.did_mount_async()
    
    def did_mount_async(self):
        """Load data asynchronously when the view is mounted"""
        # Create event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.create_task(self.load_newsletter())
    
    async def load_newsletter(self):
        """Load newsletter details from the API"""
        # Fetch newsletter
        newsletter, error = await self.api_client.get_newsletter_detail(self.newsletter_id)
        
        # Clear loading indicator
        self.content_column.controls.clear()
        
        if newsletter:
            title = newsletter.get("title", "Untitled")
            subtitle = newsletter.get("subtitle", "")
            content = newsletter.get("content", "")
            published_at = newsletter.get("publishedAt", "")
            created_by = newsletter.get("createdBy", {})
            categories = newsletter.get("categories", [])
            cover_image = newsletter.get("coverImage", "")
            events = newsletter.get("events", [])
            
            # Format date if available
            date_text = ""
            if published_at:
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                    date_text = date_obj.strftime("%B %d, %Y")
                except Exception:
                    date_text = published_at
            
            # Author information
            author_name = f"{created_by.get('firstName', '')} {created_by.get('lastName', '')}".strip()
            if not author_name:
                author_name = created_by.get('email', 'Unknown')
            
            # Add newsletter header
            self.content_column.controls.extend([
                # Cover image
                Image(
                    src=cover_image,
                    fit=ft.ImageFit.COVER,
                    width=400,
                    height=200,
                    border_radius=ft.border_radius.all(8),
                ) if cover_image else Container(height=0),
                
                # Title and metadata
                Container(height=10),
                Text(
                    title,
                    size=24,
                    weight=ft.FontWeight.BOLD,
                    color=ft.Colors.BLUE_900,
                ),
                Container(height=5),
                Text(
                    subtitle,
                    size=18,
                    weight=ft.FontWeight.W400,
                    color=ft.Colors.BLUE_GREY_700,
                    visible=bool(subtitle),
                ),
                Container(height=10),
                Row(
                    [
                        Row(
                            [
                                Icon(
                                    name=ft.Icons.CALENDAR_TODAY,
                                    size=16,
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
                        Row(
                            [
                                Icon(
                                    name=ft.Icons.PERSON,
                                    size=16,
                                    color=ft.Colors.BLUE_GREY_600,
                                ),
                                Text(
                                    author_name,
                                    size=14,
                                    color=ft.Colors.BLUE_GREY_600,
                                ),
                            ],
                            spacing=5,
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                
                # Categories
                Container(height=10),
                Row(
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
                            margin=ft.margin.only(right=5),
                        )
                        for category in categories
                    ],
                    wrap=True,
                    spacing=0,
                ) if categories else Container(height=0),
                
                # Divider
                Container(height=15),
                Divider(height=1, color=ft.Colors.BLUE_GREY_200),
                Container(height=15),
                
                # Content
                self.format_content(content),
            ])
            
            # Add related events if any
            if events:
                self.content_column.controls.extend([
                    Container(height=20),
                    Text(
                        "Related Events",
                        size=18,
                        weight=ft.FontWeight.W500,
                        color=ft.Colors.BLUE_700,
                    ),
                    Container(height=10),
                ])
                
                for event in events:
                    self.content_column.controls.append(self.create_event_card(event))
        else:
            self.content_column.controls.append(
                Container(
                    content=Column(
                        [
                            Icon(
                                name=ft.Icons.ERROR_OUTLINE,
                                size=40,
                                color=ft.Colors.RED_400,
                            ),
                            Container(height=10),
                            Text(
                                error or "Newsletter not found",
                                size=16,
                                text_align=ft.TextAlign.CENTER,
                                color=ft.Colors.RED_400,
                            ),
                            Container(height=20),
                            ElevatedButton(
                                "Back to Newsletters",
                                on_click=self.go_back,
                            ),
                        ],
                        horizontal_alignment=CrossAxisAlignment.CENTER,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=40),
                )
            )
        
        self.update()
    
    def format_content(self, content):
        """Format the newsletter content for display"""
        # In a real app, you might parse markdown or HTML here
        # For now, we'll just split by newlines and create paragraphs
        paragraphs = content.split("\n\n")
        
        content_column = Column(spacing=15)
        
        for paragraph in paragraphs:
            if paragraph.strip():
                content_column.controls.append(
                    Text(
                        paragraph.strip(),
                        size=16,
                        color=ft.Colors.BLUE_GREY_900,
                    )
                )
        
        return content_column
    
    def create_event_card(self, event):
        """Create a card for a related event"""
        title = event.get("title", "Untitled")
        location = event.get("location", "")
        start_date = event.get("startDate", "")
        end_date = event.get("endDate", "")
        
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
        
        return Card(
            content=Container(
                content=Row(
                    [
                        Container(
                            content=Icon(
                                name=ft.Icons.EVENT,
                                color=ft.Colors.BLUE_700,
                                size=24,
                            ),
                            margin=ft.margin.only(right=10),
                        ),
                        Column(
                            [
                                Text(
                                    title,
                                    size=16,
                                    weight=ft.FontWeight.W500,
                                    color=ft.Colors.BLUE_900,
                                ),
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
                                Row(
                                    [
                                        Icon(
                                            name=ft.Icons.LOCATION_ON,
                                            size=14,
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
                            ],
                            spacing=5,
                            expand=True,
                        ),
                    ],
                ),
                padding=ft.padding.all(15),
            ),
            elevation=1,
            margin=ft.margin.only(bottom=10),
        )
    
    def go_back(self, e=None):
        """Navigate back to the newsletters list"""
        self.app.page.go("/newsletters")
