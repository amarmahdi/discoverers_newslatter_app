import flet as ft
from flet import (
    Column, Container, Card, Row, Text, 
    IconButton, Icon, MainAxisAlignment, 
    CrossAxisAlignment, ProgressRing, 
    ButtonStyle, padding,
    Divider, Image, ElevatedButton
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
        
        # Selected tab index for filtering newsletters
        self.selected_tab_index = 0
        
        # Button style for tab buttons
        button_style = ButtonStyle(
            color={"selected": "#FFFFFF", "":""},
            bgcolor={"selected": "#2196F3", "":""},
            padding=10,
        )
        
        # Create filter buttons instead of tabs
        self.filter_buttons = Row(
            controls=[
                ElevatedButton(
                    text="All",
                    icon="all_inbox",
                    style=button_style,
                    data=0,  # Use data to track tab index
                    on_click=self.tab_button_clicked,
                    bgcolor="#2196F3" if self.selected_tab_index == 0 else "#BBDEFB",
                    color="#FFFFFF" if self.selected_tab_index == 0 else "#0D47A1",
                ),
                ElevatedButton(
                    text="Recent",
                    icon="new_releases",
                    style=button_style,
                    data=1,
                    on_click=self.tab_button_clicked,
                    bgcolor="#2196F3" if self.selected_tab_index == 1 else "#BBDEFB",
                    color="#FFFFFF" if self.selected_tab_index == 1 else "#0D47A1",
                ),
                ElevatedButton(
                    text="Archived",
                    icon="archive",
                    style=button_style,
                    data=2,
                    on_click=self.tab_button_clicked,
                    bgcolor="#2196F3" if self.selected_tab_index == 2 else "#BBDEFB",
                    color="#FFFFFF" if self.selected_tab_index == 2 else "#0D47A1",
                ),
            ],
            spacing=10,
        )
        
        # Data loading indicator
        self.loading = ProgressRing(width=16, height=16, stroke_width=2)
        
        # Newsletter list container
        self.newsletters_column = Column(
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        # Placeholder for when no newsletters are available
        self.empty_state = Container(
            content=Column(
                [
                    Icon(
                        name="inbox_outlined",
                        size=64,
                        color="#B0BEC5",  # BLUE_GREY_200
                    ),
                    Text(
                        "No newsletters available",
                        color="#78909C",  # BLUE_GREY_400
                        size=16,
                        weight="w500",
                    ),
                ],
                horizontal_alignment=CrossAxisAlignment.CENTER,
                spacing=10,
            ),
            alignment=ft.alignment.center,
            expand=True,
        )
        
        # Build the UI
        self.content = Column(
            [
                # Header with search and filters
                Row(
                    [
                        Text(
                            "Newsletters",
                            size=24,
                            weight="bold",
                        ),
                        IconButton(
                            icon="search",
                            icon_color="#78909C",  # BLUE_GREY_400
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                
                # Filter buttons
                self.filter_buttons,
                
                # Newsletter list
                self.newsletters_column,
            ],
            spacing=20,
            expand=True,
        )
        
        # Load newsletters when view is created
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.create_task(self.load_newsletters(filter_featured=False))
    
    def tab_button_clicked(self, e):
        # Set selected tab index based on button data
        self.selected_tab_index = e.control.data
        
        # Update button colors based on selection
        for button in self.filter_buttons.controls:
            if button.data == self.selected_tab_index:
                button.bgcolor = "#2196F3"
                button.color = "#FFFFFF"
            else:
                button.bgcolor = "#BBDEFB"
                button.color = "#0D47A1"
        
        # Update the UI
        if self.page:
            self.page.update()
        
        # Load newsletters based on selected tab
        try:
            # Get the current event loop or create a new one
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
            # Filter logic based on tab index
            if self.selected_tab_index == 0:  # All newsletters
                loop.create_task(self.load_newsletters(filter_featured=False))
            elif self.selected_tab_index == 1:  # Recent newsletters
                loop.create_task(self.load_newsletters(filter_featured=False, filter_recent=True))
            elif self.selected_tab_index == 2:  # Archived newsletters
                loop.create_task(self.load_newsletters(filter_featured=False, filter_archived=True))
        except Exception as e:
            print(f"Error loading newsletters: {str(e)}")
    
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
        author_name = f"{created_by.get('first_name', '')} {created_by.get('last_name', '')}".strip()
        if not author_name:
            author_name = created_by.get('email', 'Unknown')
        
        # Category tags
        category_row = Row(
            controls=[
                Container(
                    content=Text(
                        category.get("name", ""),
                        size=12,
                        color="#FFFFFF",  # WHITE
                    ),
                    bgcolor="#42A5F5",  # BLUE_400
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
                        # Newsletter header with image if available
                        Container(
                            content=Row(
                                [
                                    # Title and date
                                    Column(
                                        [
                                            Text(
                                                title,
                                                size=18,
                                                weight="bold",
                                            ),
                                            Text(
                                                date_text,
                                                size=12,
                                                color="#78909C",  # BLUE_GREY_400
                                            ),
                                        ],
                                        spacing=5,
                                        expand=True,
                                    ),
                                    # Cover image if available
                                    Container(
                                        content=Image(
                                            src=cover_image,
                                            width=80,
                                            height=80,
                                            border_radius=ft.border_radius.all(8),
                                            fit=ft.ImageFit.COVER,
                                        ) if cover_image else None,
                                    ),
                                ],
                                alignment=MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ),
                        
                        # Subtitle if available
                        Text(
                            subtitle,
                            size=14,
                            color="#455A64",  # BLUE_GREY_700
                            weight="w500",
                        ) if subtitle else Container(height=0),
                        
                        # Newsletter content preview
                        Text(
                            content[:150] + "..." if len(content) > 150 else content,
                            size=14,
                        ),
                        
                        # Footer with categories, author info, and read button
                        Container(
                            content=Row(
                                [
                                    # Categories
                                    category_row,
                                    # Author and read button
                                    Row(
                                        [
                                            Text(
                                                f"By {author_name}",
                                                size=12,
                                                color="#78909C",  # BLUE_GREY_400
                                            ),
                                            ElevatedButton(
                                                text="Read",
                                                on_click=lambda e, id=newsletter.get("id", ""): self.view_newsletter_detail(id),
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                ],
                                alignment=MainAxisAlignment.SPACE_BETWEEN,
                                vertical_alignment=CrossAxisAlignment.CENTER,
                            ),
                            margin=ft.margin.only(top=10),
                        ),
                    ],
                    spacing=10,
                ),
                padding=15,
            ),
            elevation=2,
            margin=ft.margin.only(bottom=5),
        )
    
    async def load_newsletters(self, filter_featured=False, filter_recent=False, filter_archived=False):
        """Load newsletters from API with filtering options"""
        try:
            # Show loading indicator
            self.newsletters_column.controls = [self.loading]
            if self.page is not None:
                await self.page.update_async()
            
            # Get newsletters from API
            newsletters, error = await self.api_client.get_newsletters()
            
            # Clear the column
            self.newsletters_column.controls.clear()
            
            if error:
                # Show error message
                self.newsletters_column.controls.append(
                    Container(
                        content=Text(
                            f"Error loading newsletters: {error}",
                            color="#EF5350",  # RED_400
                        ),
                        margin=ft.margin.only(top=20),
                    )
                )
            elif not newsletters or len(newsletters) == 0:
                # Show empty state
                self.newsletters_column.controls.append(self.empty_state)
            else:
                # Apply filters
                filtered_newsletters = newsletters
                
                # Additional filtering based on parameters
                if filter_featured:
                    filtered_newsletters = [n for n in filtered_newsletters if n.get("featured", False)]
                if filter_recent:
                    # Sort by date and take most recent
                    from datetime import datetime
                    filtered_newsletters.sort(
                        key=lambda x: datetime.fromisoformat(x.get("publishedAt", "").replace('Z', '+00:00')) 
                        if x.get("publishedAt") else datetime.min,
                        reverse=True
                    )
                    filtered_newsletters = filtered_newsletters[:5]  # Take top 5 recent
                if filter_archived:
                    filtered_newsletters = [n for n in filtered_newsletters if n.get("archived", False)]
                
                # Create cards for each newsletter
                for newsletter in filtered_newsletters:
                    self.newsletters_column.controls.append(
                        self.create_newsletter_card(newsletter)
                    )
            
            # Update the UI
            if self.page is not None:
                await self.page.update_async()
                
        except Exception as e:
            print(f"Error loading newsletters: {str(e)}")
            if self.page is not None:
                self.page.snack_bar = ft.SnackBar(
                    content=Text(f"Error loading newsletters: {str(e)}"),
                    bgcolor="#EF5350",  # RED_400
                )
                self.page.snack_bar.open = True
                await self.page.update_async()
    
    def view_newsletter_detail(self, newsletter_id):
        """Navigate to newsletter detail page"""
        self.app.page.go(f"/newsletter/{newsletter_id}")


class NewsletterDetailView(Container):
    def __init__(self, app_instance, newsletter_id):
        super().__init__()
        self.app = app_instance
        self.auth_service = app_instance.auth_service
        self.api_client = ApiClient(self.auth_service)
        self.newsletter_id = newsletter_id
        self.expand = True
        self.padding = padding.only(left=20, right=20, top=20, bottom=20)
        
        # Data loading indicator
        self.loading = ProgressRing(width=24, height=24, stroke_width=2)
        
        # Newsletter content containers
        self.header = Container()
        self.content_area = Container()
        
        # Build initial UI with loading state
        self.content = Column(
            [
                # Back button
                Row(
                    [
                        IconButton(
                            icon="arrow_back",
                            on_click=self.go_back,
                        ),
                        Text(
                            "Back to Newsletters",
                            size=16,
                            color="#2196F3",  # BLUE
                        ),
                    ],
                    spacing=0,
                    vertical_alignment=CrossAxisAlignment.CENTER,
                ),
                
                # Loading indicator
                Container(
                    content=self.loading,
                    alignment=ft.alignment.center,
                    expand=True,
                ),
            ],
            spacing=20,
            expand=True,
        )
        
        # Load newsletter details
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        loop.create_task(self.load_newsletter())
    
    def go_back(self, e=None):
        """Navigate back to newsletters list"""
        self.app.page.go("/newsletters")
    
    async def load_newsletter(self):
        """Load newsletter details from API"""
        try:
            # Get newsletter from API
            newsletter, error = await self.api_client.get_newsletter_by_id(self.newsletter_id)
            
            if error:
                # Show error message
                self.content = Column(
                    [
                        # Back button
                        Row(
                            [
                                IconButton(
                                    icon="arrow_back",
                                    on_click=self.go_back,
                                ),
                                Text(
                                    "Back to Newsletters",
                                    size=16,
                                    color="#2196F3",  # BLUE
                                ),
                            ],
                            spacing=0,
                            vertical_alignment=CrossAxisAlignment.CENTER,
                        ),
                        
                        # Error message
                        Container(
                            content=Text(
                                f"Error loading newsletter: {error}",
                                color="#EF5350",  # RED_400
                                size=16,
                            ),
                            margin=ft.margin.only(top=20),
                            alignment=ft.alignment.center,
                        ),
                    ],
                    spacing=20,
                    expand=True,
                )
            elif not newsletter:
                # Newsletter not found
                self.content = Column(
                    [
                        # Back button
                        Row(
                            [
                                IconButton(
                                    icon="arrow_back",
                                    on_click=self.go_back,
                                ),
                                Text(
                                    "Back to Newsletters",
                                    size=16,
                                    color="#2196F3",  # BLUE
                                ),
                            ],
                            spacing=0,
                            vertical_alignment=CrossAxisAlignment.CENTER,
                        ),
                        
                        # Not found message
                        Container(
                            content=Text(
                                "Newsletter not found",
                                color="#78909C",  # BLUE_GREY_400
                                size=16,
                            ),
                            margin=ft.margin.only(top=20),
                            alignment=ft.alignment.center,
                        ),
                    ],
                    spacing=20,
                    expand=True,
                )
            else:
                # Extract newsletter data
                title = newsletter.get("title", "Untitled")
                subtitle = newsletter.get("subtitle", "")
                content = newsletter.get("content", "")
                published_at = newsletter.get("publishedAt", "")
                created_by = newsletter.get("createdBy", {})
                categories = newsletter.get("categories", [])
                cover_image = newsletter.get("coverImage", "")
                
                # Format date
                date_text = ""
                if published_at:
                    try:
                        from datetime import datetime
                        date_obj = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                        date_text = date_obj.strftime("%B %d, %Y")
                    except Exception:
                        date_text = published_at
                
                # Author information
                author_name = f"{created_by.get('first_name', '')} {created_by.get('last_name', '')}".strip()
                if not author_name:
                    author_name = created_by.get('email', 'Unknown')
                
                # Category tags
                category_row = Row(
                    controls=[
                        Container(
                            content=Text(
                                category.get("name", ""),
                                size=12,
                                color="#FFFFFF",  # WHITE
                            ),
                            bgcolor="#42A5F5",  # BLUE_400
                            border_radius=ft.border_radius.all(4),
                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                            margin=ft.margin.only(right=5, bottom=5),
                        )
                        for category in categories  # Show all categories
                    ],
                    wrap=True,
                    spacing=0,
                )
                
                # Build newsletter detail view
                self.content = Column(
                    [
                        # Back button
                        Row(
                            [
                                IconButton(
                                    icon="arrow_back",
                                    on_click=self.go_back,
                                ),
                                Text(
                                    "Back to Newsletters",
                                    size=16,
                                    color="#2196F3",  # BLUE
                                ),
                            ],
                            spacing=0,
                            vertical_alignment=CrossAxisAlignment.CENTER,
                        ),
                        
                        # Newsletter header
                        Container(
                            content=Column(
                                [
                                    # Title
                                    Text(
                                        title,
                                        size=24,
                                        weight="bold",
                                    ),
                                    
                                    # Subtitle if available
                                    Text(
                                        subtitle,
                                        size=18,
                                        color="#455A64",  # BLUE_GREY_700
                                    ) if subtitle else Container(height=0),
                                    
                                    # Date and author
                                    Row(
                                        [
                                            Text(
                                                date_text,
                                                size=14,
                                                color="#78909C",  # BLUE_GREY_400
                                            ),
                                            Text(
                                                f"By {author_name}",
                                                size=14,
                                                color="#78909C",  # BLUE_GREY_400
                                            ),
                                        ],
                                        spacing=20,
                                    ) if date_text or author_name else Container(height=0),
                                    
                                    # Categories
                                    category_row if categories else Container(height=0),
                                    
                                    # Cover image if available
                                    Image(
                                        src=cover_image,
                                        width=800,
                                        height=300,
                                        fit=ft.ImageFit.COVER,
                                        border_radius=ft.border_radius.all(8),
                                    ) if cover_image else Container(height=0),
                                ],
                                spacing=10,
                            ),
                            margin=ft.margin.only(bottom=20),
                        ),
                        
                        # Content divider
                        Divider(height=1, color="#ECEFF1"),  # BLUE_GREY_100
                        
                        # Newsletter content with scrolling
                        Container(
                            content=Text(
                                content,
                                size=16,
                                selectable=True,
                            ),
                            margin=ft.margin.only(top=20),
                            expand=True,
                        ),
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                    expand=True,
                )
            
            # Update the UI
            if self.page is not None:
                await self.page.update_async()
                
        except Exception as e:
            print(f"Error loading newsletter: {str(e)}")
            if self.page is not None:
                self.page.snack_bar = ft.SnackBar(
                    content=Text(f"Error loading newsletter: {str(e)}"),
                    bgcolor="#EF5350",  # RED_400
                )
                self.page.snack_bar.open = True
                await self.page.update_async()
