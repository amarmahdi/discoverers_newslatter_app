import flet as ft
from flet import (
    Column, Container, Card, Row, Text, 
    MainAxisAlignment, CrossAxisAlignment, ProgressRing, 
    padding, Icon, Image, TextField, ElevatedButton,
    Switch, Divider, Tab, Tabs, IconButton
)
import asyncio
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
        
        # Tabs for profile sections
        self.tabs = Tabs(
            selected_index=0,
            animation_duration=300,
            tabs=[
                Tab(
                    text="Profile",
                    icon=ft.Icons.PERSON_OUTLINE,
                    content=Container(
                        content=self.build_profile_content(),
                        padding=padding.only(top=20),
                    ),
                ),
                Tab(
                    text="Children",
                    icon=ft.Icons.CHILD_CARE,
                    content=Container(
                        content=self.build_children_content(),
                        padding=padding.only(top=20),
                    ),
                ),
                Tab(
                    text="Subscriptions",
                    icon=ft.Icons.NOTIFICATIONS_OUTLINED,
                    content=Container(
                        content=self.build_subscription_content(),
                        padding=padding.only(top=20),
                    ),
                ),
            ],
            expand=1,
        )
        
        # Build the UI
        self.content = Column(
            [
                # Page header
                Row(
                    [
                        Text(
                            "My Profile",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                            color=ft.Colors.BLUE_900,
                        ),
                    ],
                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                ),
                
                # Profile tabs
                self.tabs,
            ],
            spacing=20,
            expand=True,
        )
        
        # Load profile data on initialization
        self.did_mount_async()
    
    def did_mount_async(self):
        """Load data asynchronously when the view is mounted"""
        # Create event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Run the coroutines
        loop.create_task(self.load_profile())
        loop.create_task(self.load_subscription())
    
    def build_profile_content(self):
        """Build the profile content section"""
        self.profile_column = Column(
            [
                Container(
                    content=Row(
                        [
                            self.loading,
                            Text("Loading profile...", size=14),
                        ],
                        alignment=MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=20),
                ),
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        )
        
        return self.profile_column
    
    def build_children_content(self):
        """Build the children content section"""
        self.children_column = Column(
            [
                Container(
                    content=Row(
                        [
                            self.loading,
                            Text("Loading children...", size=14),
                        ],
                        alignment=MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=20),
                ),
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        )
        
        return self.children_column
    
    def build_subscription_content(self):
        """Build the subscription content section"""
        self.subscription_column = Column(
            [
                Container(
                    content=Row(
                        [
                            self.loading,
                            Text("Loading subscription settings...", size=14),
                        ],
                        alignment=MainAxisAlignment.CENTER,
                        spacing=10,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=20),
                ),
            ],
            spacing=15,
            scroll=ft.ScrollMode.AUTO,
        )
        
        return self.subscription_column
    
    async def load_profile(self):
        """Load profile data from the API"""
        profile, error = await self.api_client.get_user_profile()
        
        # Clear loading indicator
        self.profile_column.controls.clear()
        self.children_column.controls.clear()
        
        if profile:
            # Build profile info section
            email = profile.get("email", "")
            first_name = profile.get("firstName", "")
            last_name = profile.get("lastName", "")
            role = profile.get("role", "PARENT")
            phone_number = profile.get("phoneNumber", "")
            address = profile.get("address", "")
            profile_picture = profile.get("profilePicture", "")
            children_info = profile.get("childrenInfo", "")
            emergency_contact = profile.get("emergencyContact", "")
            position = profile.get("position", "")
            bio = profile.get("bio", "")
            children = profile.get("children", [])
            
            # Profile header with user info
            self.profile_column.controls.extend([
                Container(
                    content=Row(
                        [
                            Container(
                                content=Image(
                                    src=profile_picture,
                                    width=80,
                                    height=80,
                                    fit=ft.ImageFit.COVER,
                                    border_radius=ft.border_radius.all(40),
                                ) if profile_picture else Container(
                                    content=Text(
                                        first_name[0].upper() + last_name[0].upper() if first_name and last_name else "U",
                                        size=32,
                                        color=ft.Colors.WHITE,
                                    ),
                                    width=80,
                                    height=80,
                                    border_radius=ft.border_radius.all(40),
                                    bgcolor=ft.Colors.BLUE_500,
                                    alignment=ft.alignment.center,
                                ),
                                margin=ft.margin.only(right=15),
                            ),
                            Column(
                                [
                                    Text(
                                        f"{first_name} {last_name}",
                                        size=20,
                                        weight=ft.FontWeight.W500,
                                        color=ft.Colors.BLUE_900,
                                    ),
                                    Text(
                                        email,
                                        size=14,
                                        color=ft.Colors.BLUE_GREY_600,
                                    ),
                                    Container(
                                        content=Text(
                                            role.capitalize(),
                                            size=12,
                                            color=ft.Colors.WHITE,
                                            weight=ft.FontWeight.W500,
                                        ),
                                        bgcolor=ft.Colors.BLUE_700 if role == "ADMIN" else 
                                                ft.Colors.INDIGO_500 if role == "STAFF" else 
                                                ft.Colors.GREEN_700,
                                        border_radius=ft.border_radius.all(4),
                                        padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                        margin=ft.margin.only(top=5),
                                    ),
                                ],
                                spacing=2,
                            ),
                        ],
                        alignment=MainAxisAlignment.START,
                    ),
                    margin=ft.margin.only(bottom=20),
                ),
                
                # Contact information card
                Card(
                    content=Container(
                        content=Column(
                            [
                                Row(
                                    [
                                        Icon(
                                            name=ft.Icons.CONTACT_PHONE,
                                            color=ft.Colors.BLUE_700,
                                            size=20,
                                        ),
                                        Text(
                                            "Contact Information",
                                            size=16,
                                            weight=ft.FontWeight.W500,
                                            color=ft.Colors.BLUE_700,
                                        ),
                                    ],
                                    spacing=10,
                                ),
                                Divider(height=1, color=ft.Colors.BLUE_GREY_200),
                                Container(height=10),
                                
                                # Phone number
                                Row(
                                    [
                                        Text(
                                            "Phone:",
                                            size=14,
                                            color=ft.Colors.BLUE_GREY_700,
                                            weight=ft.FontWeight.W500,
                                        ),
                                        Text(
                                            phone_number or "Not provided",
                                            size=14,
                                            color=ft.Colors.BLUE_GREY_800,
                                        ),
                                    ],
                                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                Container(height=10),
                                
                                # Address
                                Row(
                                    [
                                        Text(
                                            "Address:",
                                            size=14,
                                            color=ft.Colors.BLUE_GREY_700,
                                            weight=ft.FontWeight.W500,
                                        ),
                                    ],
                                ),
                                Container(height=5),
                                Text(
                                    address or "Not provided",
                                    size=14,
                                    color=ft.Colors.BLUE_GREY_800,
                                ),
                                
                                # Emergency contact for parents
                                Container(height=10),
                                Row(
                                    [
                                        Text(
                                            "Emergency Contact:",
                                            size=14,
                                            color=ft.Colors.BLUE_GREY_700,
                                            weight=ft.FontWeight.W500,
                                        ),
                                    ],
                                    visible=role == "PARENT",
                                ),
                                Container(
                                    content=Text(
                                        emergency_contact or "Not provided",
                                        size=14,
                                        color=ft.Colors.BLUE_GREY_800,
                                    ),
                                    visible=role == "PARENT",
                                ),
                                
                                # Position and bio for staff
                                Container(
                                    content=Column(
                                        [
                                            Container(height=10),
                                            Row(
                                                [
                                                    Text(
                                                        "Position:",
                                                        size=14,
                                                        color=ft.Colors.BLUE_GREY_700,
                                                        weight=ft.FontWeight.W500,
                                                    ),
                                                    Text(
                                                        position or "Not specified",
                                                        size=14,
                                                        color=ft.Colors.BLUE_GREY_800,
                                                    ),
                                                ],
                                                alignment=MainAxisAlignment.SPACE_BETWEEN,
                                            ),
                                            Container(height=10),
                                            Row(
                                                [
                                                    Text(
                                                        "Bio:",
                                                        size=14,
                                                        color=ft.Colors.BLUE_GREY_700,
                                                        weight=ft.FontWeight.W500,
                                                    ),
                                                ],
                                            ),
                                            Container(height=5),
                                            Text(
                                                bio or "No bio provided",
                                                size=14,
                                                color=ft.Colors.BLUE_GREY_800,
                                            ),
                                        ],
                                    ),
                                    visible=role in ["STAFF", "ADMIN"],
                                ),
                                
                                # Edit button
                                Container(height=15),
                                ElevatedButton(
                                    content=Row(
                                        [
                                            Icon(ft.Icons.EDIT),
                                            Text("Edit Profile", size=14),
                                        ],
                                        spacing=5,
                                    ),
                                    on_click=self.edit_profile,
                                ),
                            ],
                        ),
                        padding=ft.padding.all(15),
                    ),
                ),
            ])
            
            # Build children section if user is a parent
            if role == "PARENT":
                if children:
                    for child in children:
                        self.children_column.controls.append(
                            self.create_child_card(child)
                        )
                else:
                    self.children_column.controls.append(
                        Container(
                            content=Column(
                                [
                                    Icon(
                                        name=ft.Icons.INFO_OUTLINE,
                                        size=40,
                                        color=ft.Colors.BLUE_GREY_400,
                                    ),
                                    Container(height=10),
                                    Text(
                                        "No children added to your profile yet",
                                        size=16,
                                        text_align=ft.TextAlign.CENTER,
                                    ),
                                    Container(height=20),
                                    ElevatedButton(
                                        "Add Child",
                                        icon=ft.Icons.ADD,
                                        on_click=self.add_child,
                                    ),
                                ],
                                horizontal_alignment=CrossAxisAlignment.CENTER,
                            ),
                            alignment=ft.alignment.center,
                            margin=ft.margin.only(top=40),
                        )
                    )
            else:
                self.children_column.controls.append(
                    Container(
                        content=Text(
                            "This section is only available for parent accounts",
                            size=16,
                            text_align=ft.TextAlign.CENTER,
                            color=ft.Colors.BLUE_GREY_600,
                        ),
                        alignment=ft.alignment.center,
                        margin=ft.margin.only(top=40),
                    )
                )
        else:
            self.profile_column.controls.append(
                Container(
                    content=Text(
                        error or "Unable to load profile",
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.RED_400,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=40),
                )
            )
        
        self.update()
    
    async def load_subscription(self):
        """Load subscription data from the API"""
        subscription, error = await self.api_client.get_subscription_status()
        
        # Clear loading indicator
        self.subscription_column.controls.clear()
        
        if subscription:
            is_subscribed = subscription.get("isSubscribed", False)
            subscribed_at = subscription.get("subscribedAt", "")
            unsubscribed_at = subscription.get("unsubscribedAt", "")
            groups = subscription.get("groups", [])
            
            # Format dates if available
            subscribed_date = ""
            if subscribed_at:
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(subscribed_at.replace('Z', '+00:00'))
                    subscribed_date = date_obj.strftime("%B %d, %Y")
                except Exception:
                    subscribed_date = subscribed_at
            
            unsubscribed_date = ""
            if unsubscribed_at:
                try:
                    from datetime import datetime
                    date_obj = datetime.fromisoformat(unsubscribed_at.replace('Z', '+00:00'))
                    unsubscribed_date = date_obj.strftime("%B %d, %Y")
                except Exception:
                    unsubscribed_date = unsubscribed_at
            
            # Build subscription UI
            self.subscription_column.controls.extend([
                # Newsletter subscription toggle
                Card(
                    content=Container(
                        content=Column(
                            [
                                Row(
                                    [
                                        Icon(
                                            name=ft.Icons.MAIL_OUTLINE,
                                            color=ft.Colors.BLUE_700,
                                            size=20,
                                        ),
                                        Text(
                                            "Newsletter Subscription",
                                            size=16,
                                            weight=ft.FontWeight.W500,
                                            color=ft.Colors.BLUE_700,
                                        ),
                                    ],
                                    spacing=10,
                                ),
                                Divider(height=1, color=ft.Colors.BLUE_GREY_200),
                                Container(height=10),
                                
                                Row(
                                    [
                                        Text(
                                            "Receive newsletters and announcements",
                                            size=14,
                                            color=ft.Colors.BLUE_GREY_800,
                                        ),
                                        Switch(
                                            value=is_subscribed,
                                            active_color=ft.Colors.BLUE_700,
                                            on_change=self.toggle_subscription,
                                        ),
                                    ],
                                    alignment=MainAxisAlignment.SPACE_BETWEEN,
                                ),
                                
                                Container(
                                    content=Text(
                                        f"Subscribed since: {subscribed_date}" if is_subscribed else
                                        f"Unsubscribed since: {unsubscribed_date}" if unsubscribed_date else
                                        "Not subscribed to newsletters",
                                        size=12,
                                        color=ft.Colors.BLUE_GREY_600,
                                        italic=True,
                                    ),
                                    margin=ft.margin.only(top=5),
                                ),
                            ],
                        ),
                        padding=ft.padding.all(15),
                    ),
                ),
                
                # Subscription groups
                Card(
                    content=Container(
                        content=Column(
                            [
                                Row(
                                    [
                                        Icon(
                                            name=ft.Icons.CATEGORY,
                                            color=ft.Colors.BLUE_700,
                                            size=20,
                                        ),
                                        Text(
                                            "Subscription Categories",
                                            size=16,
                                            weight=ft.FontWeight.W500,
                                            color=ft.Colors.BLUE_700,
                                        ),
                                    ],
                                    spacing=10,
                                ),
                                Divider(height=1, color=ft.Colors.BLUE_GREY_200),
                                Container(height=10),
                                
                                Text(
                                    "Choose the types of newsletters you want to receive:",
                                    size=14,
                                    color=ft.Colors.BLUE_GREY_800,
                                ),
                                Container(height=10),
                                
                                # Show subscription groups if any
                                Column(
                                    controls=[
                                        Row(
                                            [
                                                Text(
                                                    group.get("name", ""),
                                                    size=14,
                                                    color=ft.Colors.BLUE_GREY_800,
                                                ),
                                                ft.Checkbox(
                                                    value=True,
                                                    label="",
                                                    disabled=not is_subscribed,
                                                ),
                                            ],
                                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                                        )
                                        for group in groups
                                    ] if groups else [
                                        Text(
                                            "No subscription categories available",
                                            size=14,
                                            color=ft.Colors.BLUE_GREY_600,
                                            italic=True,
                                        )
                                    ],
                                    spacing=10,
                                ),
                                
                                # Save button
                                Container(height=15),
                                ElevatedButton(
                                    content=Row(
                                        [
                                            Icon(ft.Icons.SAVE),
                                            Text("Save Preferences", size=14),
                                        ],
                                        spacing=5,
                                    ),
                                    disabled=not is_subscribed,
                                    on_click=self.save_subscription_preferences,
                                ),
                            ],
                        ),
                        padding=ft.padding.all(15),
                    ),
                ),
            ])
        else:
            self.subscription_column.controls.append(
                Container(
                    content=Text(
                        error or "Unable to load subscription settings",
                        size=16,
                        text_align=ft.TextAlign.CENTER,
                        color=ft.Colors.RED_400,
                    ),
                    alignment=ft.alignment.center,
                    margin=ft.margin.only(top=40),
                )
            )
        
        self.update()
    
    def create_child_card(self, child):
        """Create a card for a child"""
        first_name = child.get("firstName", "")
        last_name = child.get("lastName", "")
        date_of_birth = child.get("dateOfBirth", "")
        allergies = child.get("allergies", "")
        medical_notes = child.get("medicalNotes", "")
        photo = child.get("photo", "")
        group = child.get("group", "")
        
        # Format date of birth if available
        dob_text = ""
        age_text = ""
        if date_of_birth:
            try:
                from datetime import datetime, date
                dob_obj = datetime.fromisoformat(date_of_birth.replace('Z', '+00:00'))
                dob_text = dob_obj.strftime("%B %d, %Y")
                
                # Calculate age
                today = date.today()
                age = today.year - dob_obj.year - ((today.month, today.day) < (dob_obj.month, dob_obj.day))
                age_text = f"{age} years old"
            except Exception:
                dob_text = date_of_birth
        
        return Card(
            content=Container(
                content=Column(
                    [
                        Row(
                            [
                                Container(
                                    content=Image(
                                        src=photo,
                                        width=60,
                                        height=60,
                                        fit=ft.ImageFit.COVER,
                                        border_radius=ft.border_radius.all(30),
                                    ) if photo else Container(
                                        content=Text(
                                            first_name[0].upper(),
                                            size=24,
                                            color=ft.Colors.WHITE,
                                        ),
                                        width=60,
                                        height=60,
                                        border_radius=ft.border_radius.all(30),
                                        bgcolor=ft.Colors.BLUE_500,
                                        alignment=ft.alignment.center,
                                    ),
                                    margin=ft.margin.only(right=15),
                                ),
                                Column(
                                    [
                                        Text(
                                            f"{first_name} {last_name}",
                                            size=18,
                                            weight=ft.FontWeight.W500,
                                            color=ft.Colors.BLUE_900,
                                        ),
                                        Text(
                                            age_text,
                                            size=14,
                                            color=ft.Colors.BLUE_GREY_600,
                                        ),
                                        Container(
                                            content=Text(
                                                group or "No group assigned",
                                                size=12,
                                                color=ft.Colors.WHITE,
                                                weight=ft.FontWeight.W500,
                                            ),
                                            bgcolor=ft.Colors.BLUE_700 if group else ft.Colors.BLUE_GREY_400,
                                            border_radius=ft.border_radius.all(4),
                                            padding=ft.padding.symmetric(horizontal=8, vertical=4),
                                            margin=ft.margin.only(top=5),
                                        ),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                IconButton(
                                    icon=ft.Icons.EDIT,
                                    tooltip="Edit child information",
                                    on_click=lambda e, id=child.get("id"): self.edit_child(id),
                                ),
                            ],
                            alignment=MainAxisAlignment.START,
                        ),
                        
                        # Child details
                        Container(height=10),
                        Divider(height=1, color=ft.Colors.BLUE_GREY_200),
                        Container(height=10),
                        
                        # Date of birth
                        Row(
                            [
                                Text(
                                    "Date of Birth:",
                                    size=14,
                                    color=ft.Colors.BLUE_GREY_700,
                                    weight=ft.FontWeight.W500,
                                ),
                                Text(
                                    dob_text or "Not provided",
                                    size=14,
                                    color=ft.Colors.BLUE_GREY_800,
                                ),
                            ],
                            alignment=MainAxisAlignment.SPACE_BETWEEN,
                        ),
                        
                        # Allergies
                        Container(height=10),
                        Row(
                            [
                                Text(
                                    "Allergies:",
                                    size=14,
                                    color=ft.Colors.BLUE_GREY_700,
                                    weight=ft.FontWeight.W500,
                                ),
                            ],
                        ),
                        Container(height=5),
                        Text(
                            allergies or "None",
                            size=14,
                            color=ft.Colors.BLUE_GREY_800,
                        ),
                        
                        # Medical notes
                        Container(height=10),
                        Row(
                            [
                                Text(
                                    "Medical Notes:",
                                    size=14,
                                    color=ft.Colors.BLUE_GREY_700,
                                    weight=ft.FontWeight.W500,
                                ),
                            ],
                        ),
                        Container(height=5),
                        Text(
                            medical_notes or "None",
                            size=14,
                            color=ft.Colors.BLUE_GREY_800,
                        ),
                    ],
                ),
                padding=ft.padding.all(15),
            ),
            elevation=1,
            margin=ft.margin.only(bottom=15),
        )
    
    def edit_profile(self, e):
        """Open profile edit form"""
        # This would show a dialog or navigate to edit profile page
        self.app.page.snack_bar = ft.SnackBar(
            content=Text("Profile editing is not implemented in this demo"),
            action="OK",
        )
        self.app.page.snack_bar.open = True
        self.app.page.update()
    
    def add_child(self, e):
        """Open form to add a new child"""
        # This would show a dialog or navigate to add child page
        self.app.page.snack_bar = ft.SnackBar(
            content=Text("Adding children is not implemented in this demo"),
            action="OK",
        )
        self.app.page.snack_bar.open = True
        self.app.page.update()
    
    def edit_child(self, child_id):
        """Open form to edit a child's information"""
        # This would show a dialog or navigate to edit child page
        self.app.page.snack_bar = ft.SnackBar(
            content=Text("Child editing is not implemented in this demo"),
            action="OK",
        )
        self.app.page.snack_bar.open = True
        self.app.page.update()
    
    def toggle_subscription(self, e):
        """Toggle newsletter subscription"""
        is_subscribed = e.control.value
        
        async def update_subscription():
            success, message = await self.api_client.update_subscription(is_subscribed)
            
            if success:
                self.app.page.snack_bar = ft.SnackBar(
                    content=Text(
                        "Successfully subscribed to newsletters" if is_subscribed else
                        "Successfully unsubscribed from newsletters"
                    ),
                    action="OK",
                )
            else:
                # Revert the switch if update failed
                e.control.value = not is_subscribed
                self.app.page.snack_bar = ft.SnackBar(
                    content=Text(f"Failed to update subscription: {message}"),
                    action="OK",
                )
            
            self.app.page.snack_bar.open = True
            self.app.page.update()
            
            # Reload subscription data
            await self.load_subscription()
        
        # Create event loop if needed
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
        # Run the coroutine
        loop.create_task(update_subscription())
    
    def save_subscription_preferences(self, e):
        """Save subscription group preferences"""
        self.app.page.snack_bar = ft.SnackBar(
            content=Text("Subscription preferences saved"),
            action="OK",
        )
        self.app.page.snack_bar.open = True
        self.app.page.update()
