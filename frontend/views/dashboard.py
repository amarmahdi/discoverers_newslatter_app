import flet as ft
from flet import (
    Column, Container, Card, Row, Text, 
    IconButton, Icon, MainAxisAlignment, 
    CrossAxisAlignment, ProgressRing, padding, 
    BoxShadow, alignment, ScrollMode,
    TextField, ElevatedButton, ButtonStyle,
    margin, CircleAvatar, Divider
)
import asyncio
import datetime
from api.graphql_client import ApiClient


class DashboardView(Container):
    def __init__(self, app_instance):
        super().__init__()
        self.app = app_instance
        self.auth_service = app_instance.auth_service
        self.api_client = ApiClient(self.auth_service)
        self.expand = True
        # Reduced left padding to accommodate the sidebar
        self.padding = padding.only(left=10, right=20, top=20, bottom=0)
        
        # SAFE USER INFO HANDLING - Complete replacement
        # Get user data or empty dict if None
        self.user = self.auth_service.get_user() or {}
        
        # Initialize selected tab index
        self.selected_tab_index = 0
        
        # Safely get user initial for avatar
        first_name = self.user.get("first_name", "")
        if first_name and isinstance(first_name, str) and len(first_name.strip()) > 0:
            self.user_initial = first_name[0].upper()
        else:
            # Fallback to email initial or default
            email = self.user.get("email", "")
            if email and isinstance(email, str) and len(email.strip()) > 0:
                self.user_initial = email[0].upper()
            else:
                self.user_initial = "D"  # Default initial
        
        # Safely get display name
        if first_name and isinstance(first_name, str) and len(first_name.strip()) > 0:
            self.user_display_name = first_name
        else:
            self.user_display_name = self.user.get("email", "User")
        
        # Data loading indicator
        self.loading = ProgressRing(width=20, height=20, stroke_width=2)
        
        # Create feed containers with social media style
        self.feed_items = Column(spacing=15, scroll=ScrollMode.AUTO, expand=True)
        
        # Status update field (like posting to a social feed)
        self.status_field = TextField(
            hint_text="Share an update or announcement...",
            border_radius=10,
            min_lines=2,
            max_lines=4,
            filled=True,
            bgcolor="#E3F2FD",  # BLUE_50
        )
        
        # Build the initial UI with social media layout
        self.content = Column(
            [
                # Header with user info and search
                Container(
                    content=Row(
                        [
                            # User greeting and daycare title
                            Column(
                                [
                                    Text(
                                        f"Welcome, {self.user_display_name}!",
                                        size=24,
                                        weight="bold",
                                        color="#0D47A1",  # BLUE_900
                                    ),
                                    Text(
                                        "Discoverers Daycare Community",
                                        size=16,
                                        color="#455A64",  # BLUE_GREY_700
                                    ),
                                ],
                            ),
                            # Profile avatar (right side)
                            Container(
                                content=CircleAvatar(
                                    # Use initials for avatar if no profile picture
                                    content=Text(self.user_initial),
                                    color="#FFFFFF",  # WHITE
                                    bgcolor="#2979FF",  # BLUE_ACCENT
                                ),
                                margin=margin.only(left=10),
                            ),
                        ],
                        alignment=MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    margin=margin.only(bottom=15),
                ),
                
                # Status update section - like posting to social media
                Container(
                    content=Column(
                        [
                            self.status_field,
                            Row(
                                [
                                    ElevatedButton(
                                        "Post Update",
                                        icon=ft.Icons.SEND,
                                        style=ButtonStyle(
                                            shape={
                                                "":ft.RoundedRectangleBorder(radius=8),
                                            },
                                        ),
                                        on_click=self.post_update,
                                    ),
                                ],
                                alignment=MainAxisAlignment.END,
                            ),
                        ],
                    ),
                    bgcolor="#FFFFFF",  # WHITE
                    border_radius=8,
                    padding=padding.all(15),
                    shadow=BoxShadow(
                        spread_radius=1,
                        blur_radius=10,
                        color="#E0E0E0",  # Similar to BLACK12
                    ),
                    margin=margin.only(bottom=20),
                ),
                
                # TABS REPLACEMENT: Use buttons in a row instead of Tabs to avoid type errors
                # This replaces the problematic Tabs component
                Container(
                    content=Row(
                        [
                            ElevatedButton(
                                "All Updates",
                                icon=ft.Icons.DYNAMIC_FEED,
                                data=0,
                                on_click=self.tab_button_clicked,
                                style=ButtonStyle(
                                    shape={"":ft.RoundedRectangleBorder(radius=8)},
                                ),
                            ),
                            ElevatedButton(
                                "Newsletters",
                                icon=ft.Icons.NEWSPAPER,
                                data=1,
                                on_click=self.tab_button_clicked,
                                style=ButtonStyle(
                                    shape={"":ft.RoundedRectangleBorder(radius=8)},
                                ),
                            ),
                            ElevatedButton(
                                "Announcements",
                                icon=ft.Icons.ANNOUNCEMENT,
                                data=2,
                                on_click=self.tab_button_clicked,
                                style=ButtonStyle(
                                    shape={"":ft.RoundedRectangleBorder(radius=8)},
                                ),
                            ),
                            ElevatedButton(
                                "Events",
                                icon=ft.Icons.EVENT,
                                data=3,
                                on_click=self.tab_button_clicked,
                                style=ButtonStyle(
                                    shape={"":ft.RoundedRectangleBorder(radius=8)},
                                ),
                            ),
                        ],
                        spacing=10,
                    ),
                    padding=padding.only(bottom=10),
                ),
                
                Divider(height=1, color="#ECEFF1"),  # BLUE_GREY_100
                
                # Main feed area
                Container(
                    content=self.feed_items,
                    expand=True,
                    margin=margin.only(top=10),
                ),
            ],
            spacing=0,
            expand=True,
        )
        
        # Don't load data in __init__, will be handled by the parent view
        
    async def did_mount_async(self):
        """Load data asynchronously when the view is mounted"""
        # Display loading indicator
        self.feed_items.controls = [self.loading]
        if self.page is not None:
            await self.update_async()
        
        async def load_data():
            try:
                # Load all data types for the feed
                newsletters, news_error = await self.api_client.get_newsletters()
                announcements, announcement_error = await self.api_client.get_announcements()
                events, events_error = await self.api_client.get_upcoming_events()
                
                # Log any errors
                if news_error:
                    print(f"Error loading newsletters: {news_error}")
                if announcement_error:
                    print(f"Error loading announcements: {announcement_error}")
                if events_error:
                    print(f"Error loading events: {events_error}")
                
                # Ensure we have lists (handle None cases)
                newsletters = newsletters or []
                announcements = announcements or []
                events = events or []
                
                # Combine all items into a single feed with timestamps
                feed_items = []
                
                # Add newsletters to feed with preview content
                if newsletters:
                    for item in newsletters:
                        item['type'] = 'newsletter'
                        item['timestamp'] = item.get('publishedAt', '')
                        # Add a preview of the content
                        content = item.get('content', '')
                        if content and len(content) > 150:
                            item['preview'] = content[:150] + '...'
                        else:
                            item['preview'] = content
                        feed_items.append(item)
                
                # Add announcements to feed
                if announcements:
                    for item in announcements:
                        item['type'] = 'announcement'
                        item['timestamp'] = item.get('createdAt', '')
                        feed_items.append(item)
                
                # Add events to feed
                if events:
                    for item in events:
                        item['type'] = 'event'
                        item['timestamp'] = item.get('date', '')
                        feed_items.append(item)
                
                # Sort all items by timestamp (newest first)
                feed_items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                
                # Update the feed with the loaded items
                await self.update_feed(feed_items, news_error, announcement_error, events_error)
            except Exception as e:
                print(f"Error loading dashboard data: {e}")
                # Show error state
                self.feed_items.controls = [
                    Container(
                        content=Text(f"Error loading data: {str(e)}"),
                        alignment=alignment.center,
                        padding=padding.all(30),
                    )
                ]
                self.update()
        
        # Start the async task with proper event loop handling
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        loop.create_task(load_data())
    
    async def update_feed(self, feed_items, news_error=None, announcement_error=None, events_error=None):
        """Update the feed with the given items"""
        try:
            # Clear existing items
            self.feed_items.controls = []
            
            # Add error messages if any
            if news_error:
                self.feed_items.controls.append(
                    Container(
                        content=Text(f"Error loading newsletters: {news_error}", color="#F44336"),  
                        padding=padding.all(10),
                        bgcolor="#FFEBEE",  
                        border_radius=8,
                        margin=margin.only(bottom=10),
                    )
                )
            
            if announcement_error:
                self.feed_items.controls.append(
                    Container(
                        content=Text(f"Error loading announcements: {announcement_error}", color="#F44336"),  
                        padding=padding.all(10),
                        bgcolor="#FFEBEE",  
                        border_radius=8,
                        margin=margin.only(bottom=10),
                    )
                )
            
            if events_error:
                self.feed_items.controls.append(
                    Container(
                        content=Text(f"Error loading events: {events_error}", color="#F44336"),  
                        padding=padding.all(10),
                        bgcolor="#FFEBEE",  
                        border_radius=8,
                        margin=margin.only(bottom=10),
                    )
                )
            
            # Add feed items
            for item in feed_items:
                self.feed_items.controls.append(self.create_feed_item(item))
                
            # If no items and no errors, show a message
            if not feed_items and not any([news_error, announcement_error, events_error]):
                self.feed_items.controls.append(
                    Container(
                        content=Column(
                            [
                                Icon(
                                    name=ft.Icons.INFO_OUTLINE,
                                    size=40,
                                    color="#90A4AE",  
                                ),
                                Text(
                                    "No updates available",
                                    size=16,
                                    color="#455A64",  
                                    text_align=ft.TextAlign.CENTER,
                                ),
                            ],
                            alignment=ft.CrossAxisAlignment.CENTER,
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        alignment=ft.alignment.center,
                        padding=padding.all(30),
                    )
                )
                
            # Update the UI
            if self.page is not None:
                await self.page.update_async()
                
        except Exception as e:
            print(f"Error updating feed: {e}")
            if self.page is not None:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error updating feed: {str(e)}"),
                    bgcolor="#F44336",  
                )
                self.page.snack_bar.open = True
                await self.page.update_async()
        
    # Handle button clicks for tab navigation and page changes
    def tab_button_clicked(self, e):
        # Set selected tab index based on button data
        self.selected_tab_index = e.control.data
        
        # Navigate to appropriate page based on the selected tab
        if self.selected_tab_index == 0:  # All Updates - stay on dashboard
            # Just filter the feed for the dashboard with proper event loop handling
            try:
                # Get the current event loop or create a new one
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                # Run the filter_feed coroutine    
                loop.create_task(self.filter_feed())
            except Exception as e:
                print(f"Error filtering feed: {str(e)}")
        elif self.selected_tab_index == 1:  # Newsletters
            # Navigate to newsletters page
            self.view_all_newsletters()
        elif self.selected_tab_index == 2:  # Announcements
            # Navigate to announcements page
            self.view_all_announcements()
        elif self.selected_tab_index == 3:  # Events
            # Navigate to events page
            self.view_all_events()
    
    # Separate method for filtering feed based on selected tab
    async def filter_feed(self):
        try:
            # Show loading indicator
            self.feed_items.controls = [self.loading]
            if self.page is not None:
                await self.page.update_async()
            
            # Get all data types
            newsletters, news_error = await self.api_client.get_newsletters()
            announcements, announcement_error = await self.api_client.get_announcements()
            events, events_error = await self.api_client.get_upcoming_events()
            
            # Filter based on tab
            feed_items = []
            
            if self.selected_tab_index == 0:  # All Updates
                # Add all content types
                if newsletters:
                    for item in newsletters:
                        item['type'] = 'newsletter'
                        item['timestamp'] = item.get('publishedAt', '')
                        # Add preview for better readability
                        content = item.get('content', '')
                        if content and len(content) > 150:
                            item['preview'] = content[:150] + '...'
                        else:
                            item['preview'] = content
                        feed_items.append(item)
                        
                if announcements:
                    for item in announcements:
                        item['type'] = 'announcement'
                        item['timestamp'] = item.get('createdAt', '')
                        feed_items.append(item)
                        
                if events:
                    for item in events:
                        item['type'] = 'event'
                        item['timestamp'] = item.get('startDate', '')
                        feed_items.append(item)
                        
            elif self.selected_tab_index == 1:  # Newsletters
                if newsletters:
                    for item in newsletters:
                        item['type'] = 'newsletter'
                        item['timestamp'] = item.get('publishedAt', '')
                        content = item.get('content', '')
                        if content and len(content) > 150:
                            item['preview'] = content[:150] + '...'
                        else:
                            item['preview'] = content
                        feed_items.append(item)
                        
            elif self.selected_tab_index == 2:  # Announcements
                if announcements:
                    for item in announcements:
                        item['type'] = 'announcement'
                        item['timestamp'] = item.get('createdAt', '')
                        feed_items.append(item)
                        
            elif self.selected_tab_index == 3:  # Events
                if events:
                    for item in events:
                        item['type'] = 'event'
                        item['timestamp'] = item.get('startDate', '')
                        feed_items.append(item)
            
            # Sort by timestamp
            feed_items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
            
            # Update the feed with the filtered items
            await self.update_feed(feed_items, news_error, announcement_error, events_error)
            
        except Exception as e:
            print(f"Error filtering content: {e}")
            if self.page is not None:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Error filtering content: {str(e)}"),
                    bgcolor="#F44336",  
                )
                self.page.snack_bar.open = True
                await self.page.update_async()
        
    async def post_update(self, e):
        """Handle posting a status update as an announcement"""
        if not self.status_field.value:
            return
            
        # Show loading state on button
        e.control.disabled = True
        e.control.text = "Posting..."
        if hasattr(e.control, 'update'):
            await e.control.update_async()
        
        try:
            # Create the announcement with default priority (MEDIUM) and no expiry
            announcement, error = await self.api_client.create_announcement(
                title="Update from " + self.user_display_name,
                content=self.status_field.value,
                priority="MEDIUM",
                expiry_date=None
            )
            
            if error:
                if self.page is not None:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text(f"Error creating announcement: {error}"),
                        bgcolor="#F44336",  
                    )
                    self.page.snack_bar.open = True
                    await self.page.update_async()
            else:
                # Clear the input field
                self.status_field.value = ""
                
                # Show success message
                if self.page is not None:
                    self.page.snack_bar = ft.SnackBar(
                        content=ft.Text("Announcement posted successfully!"),
                        bgcolor="#4CAF50",  
                    )
                    self.page.snack_bar.open = True
                    await self.page.update_async()
                
                # Refresh the feed by reloading the data
                try:
                    # Show loading indicator
                    self.feed_items.controls = [self.loading]
                    if self.page is not None:
                        await self.page.update_async()
                    
                    # Reload all data
                    newsletters, news_error = await self.api_client.get_newsletters()
                    announcements, announcement_error = await self.api_client.get_announcements()
                    events, events_error = await self.api_client.get_upcoming_events()
                    
                    # Combine and sort all items
                    feed_items = []
                    
                    if newsletters:
                        for item in newsletters:
                            item['type'] = 'newsletter'
                            item['timestamp'] = item.get('publishedAt', '')
                            content = item.get('content', '')
                            if content and len(content) > 150:
                                item['preview'] = content[:150] + '...'
                            else:
                                item['preview'] = content
                            feed_items.append(item)
                    
                    if announcements:
                        for item in announcements:
                            item['type'] = 'announcement'
                            item['timestamp'] = item.get('createdAt', '')
                            feed_items.append(item)
                    
                    if events:
                        for item in events:
                            item['type'] = 'event'
                            item['timestamp'] = item.get('startDate', '')
                            feed_items.append(item)
                    
                    # Sort by timestamp
                    feed_items.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                    
                    # Update the feed
                    await self.update_feed(feed_items, news_error, announcement_error, events_error)
                    
                except Exception as load_error:
                    print(f"Error refreshing feed: {load_error}")
                    if self.page is not None:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"Posted successfully but couldn't refresh feed: {str(load_error)}"),
                            bgcolor="#FF9800",  
                        )
                        self.page.snack_bar.open = True
                        await self.page.update_async()
                
        except Exception as e:
            print(f"Error in post_update: {e}")
            if self.page is not None:
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"An error occurred: {str(e)}"),
                    bgcolor="#F44336",  
                )
                self.page.snack_bar.open = True
                await self.page.update_async()
                
        finally:
            # Reset the button state
            if hasattr(e, 'control'):
                e.control.disabled = False
                e.control.text = "Post Update"
                if hasattr(e.control, 'update'):
                    await e.control.update_async()
            
            # Ensure page is updated
            if self.page is not None:
                await self.page.update_async()
    
    def create_feed_item(self, item):
        """Create a social media style card for a feed item"""
        item_type = item.get('type', '')
        title = item.get('title', 'Untitled')
        timestamp = item.get('timestamp', '')
        author_name = item.get('author', {}).get('name', 'Admin')
        preview_content = item.get('preview', '')
        content = item.get('content', preview_content)  # Use preview_content as fallback
        
        # Format the timestamp
        date_text = "Today"
        if timestamp:
            try:
                # Convert to readable format
                date_obj = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                date_text = date_obj.strftime("%b %d, %Y")
            except Exception:
                date_text = timestamp
        
        # Create appropriate icons and badges based on content type
        if item_type == 'newsletter':
            icon = ft.Icons.NEWSPAPER
            badge_text = "Newsletter"
            badge_color = "#1976D2"  # BLUE_700
            def newsletter_click_handler(e):
                self.view_newsletter_detail(item.get('id'))
            on_click_handler = newsletter_click_handler
            
        elif item_type == 'announcement':
            icon = ft.Icons.ANNOUNCEMENT
            badge_text = "Announcement"
            badge_color = "#F57C00"  # ORANGE_700
            priority = item.get('priority', 'MEDIUM')
            if priority == 'URGENT':
                badge_color = "#D32F2F"  # RED_700
            def announcement_click_handler(e):
                self.view_all_announcements()
            on_click_handler = announcement_click_handler
            
        elif item_type == 'event':
            icon = ft.Icons.EVENT
            badge_text = "Event"
            badge_color = "#388E3C"  # GREEN_700
            def event_click_handler(e):
                self.view_all_events()
            on_click_handler = event_click_handler
            
        else:
            icon = ft.Icons.ARTICLE
            # No specific color needed for default case
            badge_text = "Update"
            badge_color = "#455A64"  # BLUE_GREY_700
            def default_click_handler(e):
                pass
            on_click_handler = default_click_handler
        
        # Create a card with social media styling
        return Container(
            content=Card(
                content=Container(
                    content=Column(
                        [
                            # Header with author info and badge
                            Row(
                                [
                                    # Author avatar and name
                                    Row(
                                        [
                                            CircleAvatar(
                                                content=Text(author_name[0].upper()),
                                                bgcolor="#90A4AE",  # BLUE_GREY_300
                                                color="#FFFFFF",  # WHITE
                                                radius=16,
                                            ),
                                            Column(
                                                [
                                                    Text(
                                                        author_name,
                                                        size=14,
                                                        weight="bold",
                                                    ),
                                                    Text(
                                                        date_text,
                                                        size=12,
                                                        color="#607D8B",  # BLUE_GREY_500
                                                    ),
                                                ],
                                                spacing=0,
                                                horizontal_alignment=CrossAxisAlignment.START,
                                            ),
                                        ],
                                        spacing=10,
                                    ),
                                    # Type badge
                                    Container(
                                        content=Row(
                                            [
                                                Icon(
                                                    name=icon,
                                                    color="#FFFFFF",  # WHITE
                                                    size=12,
                                                ),
                                                Text(
                                                    badge_text,
                                                    color="#FFFFFF",  # WHITE
                                                    size=12,
                                                    weight="w500",
                                                ),
                                            ],
                                            spacing=4,
                                        ),
                                        bgcolor=badge_color,
                                        border_radius=12,
                                        padding=padding.symmetric(horizontal=8, vertical=4),
                                    ),
                                ],
                                alignment=MainAxisAlignment.SPACE_BETWEEN,
                            ),
                            
                            # Content
                            Container(
                                content=Column(
                                    [
                                        Text(
                                            title,
                                            size=18,
                                            weight="w500",
                                            color="#0D47A1",  # BLUE_900
                                        ),
                                        Container(height=5),
                                        Text(
                                            (content or '')[:150] + ("..." if (content and len(content) > 150) else ""),
                                            size=14,
                                            color="#37474F",  # BLUE_GREY_800
                                        ) if content else Container(),
                                    ],
                                ),
                                margin=margin.symmetric(vertical=10),
                            ),
                            
                            # Actions row (like, comment, share)
                            Row(
                                [
                                    Row(
                                        [
                                            IconButton(
                                                icon=ft.Icons.THUMB_UP_OUTLINED,
                                                tooltip="Like",
                                                icon_color="#607D8B",  # BLUE_GREY_500
                                            ),
                                            Text("0", size=14, color=ft.Colors.BLUE_GREY_500),
                                        ],
                                    ),
                                    Row(
                                        [
                                            IconButton(
                                                icon=ft.Icons.COMMENT_OUTLINED,
                                                tooltip="Comment",
                                                icon_color="#607D8B",  # BLUE_GREY_500
                                            ),
                                            Text("0", size=14, color=ft.Colors.BLUE_GREY_500),
                                        ],
                                    ),
                                    IconButton(
                                        icon=ft.Icons.READ_MORE,
                                        tooltip="View details",
                                        icon_color="#1976D2",  # BLUE_700
                                        on_click=on_click_handler,
                                    ),
                                ],
                                alignment=MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ],
                    ),
                    padding=padding.all(15),
                ),
                elevation=2,
            ),
            margin=margin.only(bottom=15),
        )
    
    def create_newsletter_card(self, newsletter):
        """Create a card for a newsletter"""
        title = newsletter.get("title", "Untitled")
        subtitle = newsletter.get("subtitle", "")
        published_at = newsletter.get("publishedAt", "")
        
        # Format date if available
        date_text = ""
        if published_at:
            try:
                from datetime import datetime
                date_obj = datetime.fromisoformat(published_at.replace('Z', '+00:00'))
                date_text = date_obj.strftime("%B %d, %Y")
            except Exception:
                date_text = published_at
        
        return Card(
            content=Container(
                content=Column(
                    [
                        Row(
                            [
                                Icon(
                                    name=ft.Icons.ARTICLE_OUTLINED,
                                    color=ft.Colors.BLUE_700,
                                ),
                                Text(
                                    date_text,
                                    size=12,
                                    color="#607D8B",  # BLUE_GREY_500
                                ),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        Container(height=5),
                        Text(
                            title,
                            size=16,
                            weight="w400",
                            color="#0D47A1",  # BLUE_900
                        ),
                        Container(height=2),
                        Text(
                            subtitle or "Click to read more...",
                            size=14,
                            color="#455A64",  # BLUE_GREY_700
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                ),
                padding=ft.padding.all(15),
                on_click=lambda e: self.open_newsletter(newsletter.get("id")),
            ),
            elevation=1,
            margin=ft.margin.only(bottom=10),
        )
    
    def create_announcement_card(self, announcement):
        """Create a card for an announcement"""
        title = announcement.get("title", "Untitled")
        content = announcement.get("content", "")
        priority = announcement.get("priority", "MEDIUM")
        created_at = announcement.get("createdAt", "")
        
        # Determine color based on priority
        priority_colors = {
            "LOW": "#4CAF50",  # GREEN
            "MEDIUM": "#2196F3",  # BLUE
            "HIGH": "#FF9800",  # ORANGE
            "URGENT": "#F44336",  # RED,
        }
        priority_color = priority_colors.get(priority, "#2196F3")  # Default to BLUE
        
        # Format date if available
        date_text = ""
        if created_at:
            try:
                from datetime import datetime
                date_obj = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                date_text = date_obj.strftime("%B %d, %Y")
            except Exception:
                date_text = created_at
        
        return Card(
            content=Container(
                content=Column(
                    [
                        Row(
                            [
                                Container(
                                    content=Text(
                                        priority,
                                        size=12,
                                        color="#FFFFFF",  # WHITE
                                    ),
                                    padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                    border_radius=ft.border_radius.all(4),
                                    bgcolor=priority_color,
                                ),
                                Text(
                                    date_text,
                                    size=12,
                                    color="#607D8B",  # BLUE_GREY_500
                                ),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        Container(height=5),
                        Text(
                            title,
                            size=16,
                            weight="w400",
                            color="#0D47A1",  # BLUE_900
                        ),
                        Container(height=2),
                        Text(
                            content,
                            size=14,
                            color="#455A64",  # BLUE_GREY_700
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                ),
                padding=ft.padding.all(15),
            ),
            elevation=1,
            margin=ft.margin.only(bottom=10),
        )
    
    def create_event_card(self, event):
        """Create a card for an event"""
        title = event.get("title", "Untitled")
        description = event.get("description", "")
        location = event.get("location", "")
        start_date = event.get("startDate", "")
        end_date = event.get("endDate", "")
        
        # Format date if available
        date_text = ""
        if start_date:
            try:
                from datetime import datetime
                start_obj = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                date_text = start_obj.strftime("%B %d, %Y")
                
                if end_date:
                    end_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    if start_obj.date() != end_obj.date():
                        date_text += f" - {end_obj.strftime('%B %d, %Y')}"
                    
                time_text = f"{start_obj.strftime('%I:%M %p')}"
                if end_date:
                    end_obj = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    time_text += f" - {end_obj.strftime('%I:%M %p')}"
            except Exception:
                date_text = start_date
                time_text = ""
        else:
            date_text = "Date TBD"
            time_text = ""
        
        return Card(
            content=Container(
                content=Column(
                    [
                        Row(
                            [
                                Icon(
                                    name=ft.Icons.EVENT,
                                    color=ft.Colors.BLUE_700,
                                ),
                                Column(
                                    [
                                        Text(
                                            date_text,
                                            size=12,
                                            color="#455A64",  # BLUE_GREY_700
                                            weight="w400",
                                        ),
                                        Text(
                                            time_text,
                                            size=12,
                                            color="#607D8B",  # BLUE_GREY_500
                                        ),
                                    ],
                                    spacing=0,
                                    horizontal_alignment=CrossAxisAlignment.END,
                                ),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        Container(height=5),
                        Text(
                            title,
                            size=16,
                            weight="w400",
                            color="#0D47A1",  # BLUE_900
                        ),
                        Container(height=2),
                        Row(
                            [
                                Icon(
                                    name=ft.Icons.LOCATION_ON,
                                    color="#607D8B",  # BLUE_GREY_500
                                    size=16,
                                ),
                                Text(
                                    location,
                                    size=14,
                                    color="#455A64",  # BLUE_GREY_700
                                ),
                            ],
                            spacing=5,
                            visible=bool(location),
                        ),
                        Text(
                            description,
                            size=14,
                            color="#455A64",  # BLUE_GREY_700
                            max_lines=2,
                            overflow=ft.TextOverflow.ELLIPSIS,
                        ),
                    ],
                ),
                padding=ft.padding.all(15),
            ),
            elevation=1,
            margin=ft.margin.only(bottom=10),
        )
    
    def view_all_newsletters(self, e=None):
        """Navigate to newsletters page"""
        self.app.page.go("/newsletters")
    
    def view_newsletter_detail(self, newsletter_id):
        """Navigate to newsletter detail page"""
        self.app.page.go(f"/newsletter/{newsletter_id}")
        
    def view_all_announcements(self, e=None):
        """Navigate to announcements page"""
        self.app.page.go("/announcements")
        
    def view_all_events(self, e=None):
        """Navigate to events page"""
        self.app.page.go("/events")
    
    def open_newsletter(self, newsletter_id):
        """Open a specific newsletter"""
        if newsletter_id:
            self.app.page.go(f"/newsletter/{newsletter_id}")
