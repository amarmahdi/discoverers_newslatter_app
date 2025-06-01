from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import (
    Category, Newsletter, Announcement, Event,
    SubscriptionGroup, Subscription, NewsletterRecipient
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)


class EventInline(admin.TabularInline):
    model = Event.newsletters.through
    extra = 0
    verbose_name = _('Event')
    verbose_name_plural = _('Events')


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_by', 'created_at', 'published_at', 'featured', 'sent_to_all')
    list_filter = ('status', 'featured', 'sent_to_all', 'categories')
    search_fields = ('title', 'subtitle', 'content')
    date_hierarchy = 'created_at'
    filter_horizontal = ('categories',)
    readonly_fields = ('created_at', 'updated_at', 'published_at')
    actions = ['publish_newsletters', 'archive_newsletters']
    fieldsets = (
        (None, {'fields': ('title', 'subtitle', 'content', 'cover_image', 'created_by')}),
        (_('Status'), {'fields': ('status', 'featured', 'sent_to_all')}),
        (_('Categories'), {'fields': ('categories',)}),
        (_('Dates'), {'fields': ('created_at', 'updated_at', 'published_at')}),
    )
    inlines = [EventInline]
    
    def publish_newsletters(self, request, queryset):
        count = 0
        for newsletter in queryset.filter(status=Newsletter.Status.DRAFT):
            newsletter.publish()
            count += 1
        self.message_user(request, _(f'{count} newsletters were published successfully.'))
    publish_newsletters.short_description = _('Publish selected newsletters')
    
    def archive_newsletters(self, request, queryset):
        count = queryset.filter(status=Newsletter.Status.PUBLISHED).update(status=Newsletter.Status.ARCHIVED)
        self.message_user(request, _(f'{count} newsletters were archived successfully.'))
    archive_newsletters.short_description = _('Archive selected newsletters')


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'priority', 'created_by', 'created_at', 'expiry_date', 'is_active', 'is_expired')
    list_filter = ('priority', 'is_active', 'categories')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    filter_horizontal = ('categories',)
    readonly_fields = ('created_at', 'is_expired')
    fieldsets = (
        (None, {'fields': ('title', 'content', 'image', 'created_by')}),
        (_('Status'), {'fields': ('priority', 'is_active', 'expiry_date')}),
        (_('Categories'), {'fields': ('categories',)}),
        (_('Dates'), {'fields': ('created_at',)}),
    )
    
    def is_expired(self, obj):
        return obj.is_expired
    is_expired.boolean = True
    is_expired.short_description = _('Expired')


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'start_date', 'end_date', 'location', 'created_by', 'is_active', 'is_past')
    list_filter = ('is_active', 'categories')
    search_fields = ('title', 'description', 'location')
    date_hierarchy = 'start_date'
    filter_horizontal = ('categories', 'newsletters')
    readonly_fields = ('is_past',)
    fieldsets = (
        (None, {'fields': ('title', 'description', 'image', 'created_by')}),
        (_('Timing'), {'fields': ('start_date', 'end_date', 'location')}),
        (_('Status'), {'fields': ('is_active',)}),
        (_('Categories & Newsletters'), {'fields': ('categories', 'newsletters')}),
    )
    
    def is_past(self, obj):
        return obj.is_past
    is_past.boolean = True
    is_past.short_description = _('Past event')


@admin.register(SubscriptionGroup)
class SubscriptionGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'subscriber_count')
    search_fields = ('name', 'description')
    
    def subscriber_count(self, obj):
        return obj.subscribers.count()
    subscriber_count.short_description = _('Subscribers')


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_subscribed', 'subscribed_at', 'unsubscribed_at')
    list_filter = ('is_subscribed', 'groups')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    filter_horizontal = ('groups',)
    readonly_fields = ('subscribed_at', 'unsubscribed_at')
    actions = ['resubscribe_users', 'unsubscribe_users']
    
    def resubscribe_users(self, request, queryset):
        count = 0
        for subscription in queryset.filter(is_subscribed=False):
            subscription.resubscribe()
            count += 1
        self.message_user(request, _(f'{count} users were resubscribed successfully.'))
    resubscribe_users.short_description = _('Resubscribe selected users')
    
    def unsubscribe_users(self, request, queryset):
        count = 0
        for subscription in queryset.filter(is_subscribed=True):
            subscription.unsubscribe()
            count += 1
        self.message_user(request, _(f'{count} users were unsubscribed successfully.'))
    unsubscribe_users.short_description = _('Unsubscribe selected users')


@admin.register(NewsletterRecipient)
class NewsletterRecipientAdmin(admin.ModelAdmin):
    list_display = ('newsletter', 'user', 'sent_at', 'opened_at', 'clicked')
    list_filter = ('clicked', 'newsletter')
    search_fields = ('newsletter__title', 'user__email')
    date_hierarchy = 'sent_at'
    readonly_fields = ('sent_at', 'opened_at', 'clicked')
    
    def has_add_permission(self, request):
        return False
