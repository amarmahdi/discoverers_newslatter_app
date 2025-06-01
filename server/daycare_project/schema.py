import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required
import graphql_jwt

from accounts.models import User, Child
from newsletter.models import (
    Category, Newsletter, Announcement, Event,
    SubscriptionGroup, Subscription, NewsletterRecipient
)


# Types for accounts app
class UserType(DjangoObjectType):
    class Meta:
        model = User
        exclude = ('password',)


class ChildType(DjangoObjectType):
    class Meta:
        model = Child


# Types for newsletter app
class CategoryType(DjangoObjectType):
    class Meta:
        model = Category


class NewsletterType(DjangoObjectType):
    class Meta:
        model = Newsletter


class AnnouncementType(DjangoObjectType):
    class Meta:
        model = Announcement


class EventType(DjangoObjectType):
    class Meta:
        model = Event


class SubscriptionGroupType(DjangoObjectType):
    class Meta:
        model = SubscriptionGroup


class SubscriptionType(DjangoObjectType):
    class Meta:
        model = Subscription


class NewsletterRecipientType(DjangoObjectType):
    class Meta:
        model = NewsletterRecipient


# Queries
class Query(graphene.ObjectType):
    # User queries
    users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.ID())
    me = graphene.Field(UserType)
    
    # Child queries
    children = graphene.List(ChildType)
    child = graphene.Field(ChildType, id=graphene.ID())
    
    # Category queries
    categories = graphene.List(CategoryType)
    category = graphene.Field(CategoryType, id=graphene.ID())
    
    # Newsletter queries
    newsletters = graphene.List(NewsletterType, status=graphene.String())
    newsletter = graphene.Field(NewsletterType, id=graphene.ID())
    featured_newsletters = graphene.List(NewsletterType)
    
    # Announcement queries
    announcements = graphene.List(AnnouncementType, is_active=graphene.Boolean())
    announcement = graphene.Field(AnnouncementType, id=graphene.ID())
    
    # Event queries
    events = graphene.List(EventType, is_active=graphene.Boolean())
    event = graphene.Field(EventType, id=graphene.ID())
    upcoming_events = graphene.List(EventType)
    
    # Subscription queries
    subscription_groups = graphene.List(SubscriptionGroupType)
    my_subscription = graphene.Field(SubscriptionType)
    
    @login_required
    def resolve_users(self, info, **kwargs):
        # Only staff or admin users can see all users
        user = info.context.user
        if user.is_staff or user.is_admin:
            return User.objects.all()
        return None
    
    @login_required
    def resolve_user(self, info, id):
        # Only staff or admin users can see user details
        user = info.context.user
        if user.is_staff or user.is_admin:
            return User.objects.get(pk=id)
        return None
    
    @login_required
    def resolve_me(self, info):
        user = info.context.user
        return user
    
    @login_required
    def resolve_children(self, info):
        user = info.context.user
        if user.is_staff or user.is_admin:
            return Child.objects.all()
        elif user.is_parent:
            return Child.objects.filter(parent=user)
        return None
    
    @login_required
    def resolve_child(self, info, id):
        user = info.context.user
        if user.is_staff or user.is_admin:
            return Child.objects.get(pk=id)
        elif user.is_parent:
            return Child.objects.get(pk=id, parent=user)
        return None
    
    def resolve_categories(self, info):
        return Category.objects.all()
    
    def resolve_category(self, info, id):
        return Category.objects.get(pk=id)
    
    def resolve_newsletters(self, info, status=None):
        if status:
            return Newsletter.objects.filter(status=status)
        return Newsletter.objects.filter(status=Newsletter.Status.PUBLISHED)
    
    def resolve_newsletter(self, info, id):
        return Newsletter.objects.get(pk=id)
    
    def resolve_featured_newsletters(self, info):
        return Newsletter.objects.filter(featured=True, status=Newsletter.Status.PUBLISHED)
    
    def resolve_announcements(self, info, is_active=True):
        return Announcement.objects.filter(is_active=is_active)
    
    def resolve_announcement(self, info, id):
        return Announcement.objects.get(pk=id)
    
    def resolve_events(self, info, is_active=True):
        return Event.objects.filter(is_active=is_active)
    
    def resolve_event(self, info, id):
        return Event.objects.get(pk=id)
    
    def resolve_upcoming_events(self, info):
        from django.utils import timezone
        return Event.objects.filter(start_date__gte=timezone.now(), is_active=True)
    
    @login_required
    def resolve_subscription_groups(self, info):
        return SubscriptionGroup.objects.all()
    
    @login_required
    def resolve_my_subscription(self, info):
        user = info.context.user
        subscription, created = Subscription.objects.get_or_create(user=user)
        return subscription


# Mutations for accounts app
class CreateUserMutation(graphene.Mutation):
    user = graphene.Field(UserType)
    
    class Arguments:
        email = graphene.String(required=True)
        password = graphene.String(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        role = graphene.String()
        phone_number = graphene.String()
        address = graphene.String()
    
    def mutate(self, info, email, password, first_name, last_name, role=None, **kwargs):
        # For public registration, prevent creating ADMIN users directly.
        # STAFF users might be allowed if they need to self-register, 
        # otherwise, this check can be made stricter (e.g., allow only PARENT).
        if role == User.Role.ADMIN:
            raise Exception("Permission denied. Cannot create ADMIN users through public registration.")
        
        # If a non-admin user tries to create a STAFF user, this was previously checked by:
        # user = info.context.user (which would be an admin)
        # if role in [User.Role.STAFF, User.Role.ADMIN] and not user.is_admin:
        # For now, we allow STAFF creation via public registration as per frontend options.
        # If this needs to be restricted, further logic changes are needed, 
        # possibly by having separate mutations for admin-created users vs public sign-ups.
        
        new_user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role or User.Role.PARENT,
            **kwargs
        )
        new_user.set_password(password)
        new_user.save()
        
        return CreateUserMutation(user=new_user)


class UpdateUserMutation(graphene.Mutation):
    user = graphene.Field(UserType)
    
    class Arguments:
        id = graphene.ID(required=True)
        email = graphene.String()
        first_name = graphene.String()
        last_name = graphene.String()
        role = graphene.String()
        phone_number = graphene.String()
        address = graphene.String()
        children_info = graphene.String()
        emergency_contact = graphene.String()
        position = graphene.String()
        bio = graphene.String()
    
    @login_required
    def mutate(self, info, id, **kwargs):
        user = info.context.user
        
        # Users can update their own profiles, admins can update any user
        if str(user.id) != id and not user.is_admin:
            raise Exception("Permission denied. You can only update your own profile.")
        
        # Only admin can change role to staff or admin
        if 'role' in kwargs and kwargs['role'] in [User.Role.STAFF, User.Role.ADMIN] and not user.is_admin:
            raise Exception("Permission denied. Only admins can change roles to staff or admin.")
        
        User.objects.filter(pk=id).update(**kwargs)
        updated_user = User.objects.get(pk=id)
        
        return UpdateUserMutation(user=updated_user)


class CreateChildMutation(graphene.Mutation):
    child = graphene.Field(ChildType)
    
    class Arguments:
        parent_id = graphene.ID(required=True)
        first_name = graphene.String(required=True)
        last_name = graphene.String(required=True)
        date_of_birth = graphene.Date(required=True)
        allergies = graphene.String()
        medical_notes = graphene.String()
        group = graphene.String()
    
    @login_required
    def mutate(self, info, parent_id, **kwargs):
        user = info.context.user
        
        # Users can add children to their own profiles, staff and admins can add to any parent
        if str(user.id) != parent_id and not (user.is_staff or user.is_admin):
            raise Exception("Permission denied. You can only add children to your own profile.")
        
        parent = User.objects.get(pk=parent_id)
        if parent.role != User.Role.PARENT:
            raise Exception("Children can only be added to parent accounts.")
        
        child = Child(parent=parent, **kwargs)
        child.save()
        
        return CreateChildMutation(child=child)


# Mutations for newsletter app
class CreateNewsletterMutation(graphene.Mutation):
    newsletter = graphene.Field(NewsletterType)
    
    class Arguments:
        title = graphene.String(required=True)
        subtitle = graphene.String()
        content = graphene.String(required=True)
        status = graphene.String()
        category_ids = graphene.List(graphene.ID)
        featured = graphene.Boolean()
    
    @login_required
    def mutate(self, info, title, content, category_ids=None, **kwargs):
        user = info.context.user
        
        # Only staff and admin can create newsletters
        if not (user.is_staff or user.is_admin):
            raise Exception("Permission denied. Only staff and admins can create newsletters.")
        
        newsletter = Newsletter(
            title=title,
            content=content,
            created_by=user,
            **kwargs
        )
        newsletter.save()
        
        if category_ids:
            for cat_id in category_ids:
                category = Category.objects.get(pk=cat_id)
                newsletter.categories.add(category)
        
        return CreateNewsletterMutation(newsletter=newsletter)


class PublishNewsletterMutation(graphene.Mutation):
    newsletter = graphene.Field(NewsletterType)
    
    class Arguments:
        id = graphene.ID(required=True)
        send_to_all = graphene.Boolean()
    
    @login_required
    def mutate(self, info, id, send_to_all=False):
        user = info.context.user
        
        # Only staff and admin can publish newsletters
        if not (user.is_staff or user.is_admin):
            raise Exception("Permission denied. Only staff and admins can publish newsletters.")
        
        newsletter = Newsletter.objects.get(pk=id)
        newsletter.publish()
        
        if send_to_all:
            newsletter.sent_to_all = True
            newsletter.save()
            
            # Create recipient records for all subscribed users
            subscribed_users = User.objects.filter(
                subscriptions__is_subscribed=True
            )
            
            for recipient in subscribed_users:
                NewsletterRecipient.objects.create(
                    newsletter=newsletter,
                    user=recipient
                )
        
        return PublishNewsletterMutation(newsletter=newsletter)


class CreateAnnouncementMutation(graphene.Mutation):
    announcement = graphene.Field(AnnouncementType)
    
    class Arguments:
        title = graphene.String(required=True)
        content = graphene.String(required=True)
        priority = graphene.String()
        expiry_date = graphene.DateTime()
        category_ids = graphene.List(graphene.ID)
    
    @login_required
    def mutate(self, info, title, content, category_ids=None, **kwargs):
        user = info.context.user
        
        # Only staff and admin can create announcements
        if not (user.is_staff or user.is_admin):
            raise Exception("Permission denied. Only staff and admins can create announcements.")
        
        announcement = Announcement(
            title=title,
            content=content,
            created_by=user,
            **kwargs
        )
        announcement.save()
        
        if category_ids:
            for cat_id in category_ids:
                category = Category.objects.get(pk=cat_id)
                announcement.categories.add(category)
        
        return CreateAnnouncementMutation(announcement=announcement)


class CreateEventMutation(graphene.Mutation):
    event = graphene.Field(EventType)
    
    class Arguments:
        title = graphene.String(required=True)
        description = graphene.String(required=True)
        start_date = graphene.DateTime(required=True)
        end_date = graphene.DateTime(required=True)
        location = graphene.String()
        category_ids = graphene.List(graphene.ID)
        newsletter_ids = graphene.List(graphene.ID)
    
    @login_required
    def mutate(self, info, title, description, start_date, end_date, 
               category_ids=None, newsletter_ids=None, **kwargs):
        user = info.context.user
        
        # Only staff and admin can create events
        if not (user.is_staff or user.is_admin):
            raise Exception("Permission denied. Only staff and admins can create events.")
        
        event = Event(
            title=title,
            description=description,
            start_date=start_date,
            end_date=end_date,
            created_by=user,
            **kwargs
        )
        event.save()
        
        if category_ids:
            for cat_id in category_ids:
                category = Category.objects.get(pk=cat_id)
                event.categories.add(category)
        
        if newsletter_ids:
            for nl_id in newsletter_ids:
                newsletter = Newsletter.objects.get(pk=nl_id)
                event.newsletters.add(newsletter)
        
        return CreateEventMutation(event=event)


class UpdateSubscriptionMutation(graphene.Mutation):
    subscription = graphene.Field(SubscriptionType)
    
    class Arguments:
        is_subscribed = graphene.Boolean(required=True)
        group_ids = graphene.List(graphene.ID)
    
    @login_required
    def mutate(self, info, is_subscribed, group_ids=None):
        user = info.context.user
        
        subscription, created = Subscription.objects.get_or_create(user=user)
        
        if is_subscribed and not subscription.is_subscribed:
            subscription.resubscribe()
        elif not is_subscribed and subscription.is_subscribed:
            subscription.unsubscribe()
        
        if group_ids is not None:
            subscription.groups.clear()
            for group_id in group_ids:
                group = SubscriptionGroup.objects.get(pk=group_id)
                subscription.groups.add(group)
        
        return UpdateSubscriptionMutation(subscription=subscription)


class Mutation(graphene.ObjectType):
    # JWT Authentication mutations
    token_auth = graphql_jwt.ObtainJSONWebToken.Field()
    verify_token = graphql_jwt.Verify.Field()
    refresh_token = graphql_jwt.Refresh.Field()
    
    # User mutations
    create_user = CreateUserMutation.Field()
    update_user = UpdateUserMutation.Field()
    create_child = CreateChildMutation.Field()
    
    # Newsletter mutations
    create_newsletter = CreateNewsletterMutation.Field()
    publish_newsletter = PublishNewsletterMutation.Field()
    create_announcement = CreateAnnouncementMutation.Field()
    create_event = CreateEventMutation.Field()
    update_subscription = UpdateSubscriptionMutation.Field()


schema = graphene.Schema(query=Query, mutation=Mutation)
