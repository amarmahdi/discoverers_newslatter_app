from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from accounts.models import User


class Category(models.Model):
    """Categories for organizing newsletters and announcements."""
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    
    class Meta:
        verbose_name = _('category')
        verbose_name_plural = _('categories')
    
    def __str__(self):
        return self.name


class Newsletter(models.Model):
    """Main newsletter model for daycare communications."""
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        PUBLISHED = 'PUBLISHED', _('Published')
        ARCHIVED = 'ARCHIVED', _('Archived')
    
    title = models.CharField(_('title'), max_length=200)
    subtitle = models.CharField(_('subtitle'), max_length=200, blank=True)
    content = models.TextField(_('content'))
    cover_image = models.ImageField(upload_to='newsletter_covers/', blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_newsletters')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)
    published_at = models.DateTimeField(_('published at'), null=True, blank=True)
    status = models.CharField(_('status'), max_length=10, choices=Status.choices, default=Status.DRAFT)
    categories = models.ManyToManyField(Category, blank=True, related_name='newsletters')
    featured = models.BooleanField(_('featured'), default=False)
    sent_to_all = models.BooleanField(_('sent to all'), default=False)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('newsletter')
        verbose_name_plural = _('newsletters')
    
    def __str__(self):
        return self.title
    
    def publish(self):
        """Publish the newsletter and record the time."""
        self.status = self.Status.PUBLISHED
        self.published_at = timezone.now()
        self.save()
    
    def archive(self):
        """Archive the newsletter."""
        self.status = self.Status.ARCHIVED
        self.save()


class Announcement(models.Model):
    """Quick announcements and updates for the daycare."""
    class Priority(models.TextChoices):
        LOW = 'LOW', _('Low')
        MEDIUM = 'MEDIUM', _('Medium')
        HIGH = 'HIGH', _('High')
        URGENT = 'URGENT', _('Urgent')
    
    title = models.CharField(_('title'), max_length=200)
    content = models.TextField(_('content'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_announcements')
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    expiry_date = models.DateTimeField(_('expiry date'), null=True, blank=True)
    priority = models.CharField(_('priority'), max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    categories = models.ManyToManyField(Category, blank=True, related_name='announcements')
    image = models.ImageField(upload_to='announcement_images/', blank=True, null=True)
    is_active = models.BooleanField(_('is active'), default=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('announcement')
        verbose_name_plural = _('announcements')
    
    def __str__(self):
        return self.title
    
    @property
    def is_expired(self):
        if self.expiry_date:
            return timezone.now() > self.expiry_date
        return False


class Event(models.Model):
    """Events at the daycare to be announced in newsletters."""
    title = models.CharField(_('title'), max_length=200)
    description = models.TextField(_('description'))
    start_date = models.DateTimeField(_('start date'))
    end_date = models.DateTimeField(_('end date'))
    location = models.CharField(_('location'), max_length=200, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events')
    image = models.ImageField(upload_to='event_images/', blank=True, null=True)
    categories = models.ManyToManyField(Category, blank=True, related_name='events')
    is_active = models.BooleanField(_('is active'), default=True)
    newsletters = models.ManyToManyField(Newsletter, blank=True, related_name='events')
    
    class Meta:
        ordering = ['start_date']
        verbose_name = _('event')
        verbose_name_plural = _('events')
    
    def __str__(self):
        return self.title
    
    @property
    def is_past(self):
        return timezone.now() > self.end_date


class SubscriptionGroup(models.Model):
    """Groups for categorizing newsletter subscribers."""
    name = models.CharField(_('name'), max_length=100)
    description = models.TextField(_('description'), blank=True)
    
    def __str__(self):
        return self.name


class Subscription(models.Model):
    """Newsletter subscriptions for users."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    groups = models.ManyToManyField(SubscriptionGroup, blank=True, related_name='subscribers')
    is_subscribed = models.BooleanField(_('is subscribed'), default=True)
    subscribed_at = models.DateTimeField(_('subscribed at'), auto_now_add=True)
    unsubscribed_at = models.DateTimeField(_('unsubscribed at'), null=True, blank=True)
    
    class Meta:
        unique_together = ('user',)
        verbose_name = _('subscription')
        verbose_name_plural = _('subscriptions')
    
    def __str__(self):
        return f"{self.user.email}'s subscription"
    
    def unsubscribe(self):
        """Unsubscribe the user and record the time."""
        self.is_subscribed = False
        self.unsubscribed_at = timezone.now()
        self.save()
    
    def resubscribe(self):
        """Resubscribe the user."""
        self.is_subscribed = True
        self.unsubscribed_at = None
        self.save()


class NewsletterRecipient(models.Model):
    """Tracks which newsletters were sent to which users."""
    newsletter = models.ForeignKey(Newsletter, on_delete=models.CASCADE, related_name='recipients')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_newsletters')
    sent_at = models.DateTimeField(_('sent at'), auto_now_add=True)
    opened_at = models.DateTimeField(_('opened at'), null=True, blank=True)
    clicked = models.BooleanField(_('clicked'), default=False)
    
    class Meta:
        unique_together = ('newsletter', 'user')
        verbose_name = _('newsletter recipient')
        verbose_name_plural = _('newsletter recipients')
    
    def __str__(self):
        return f"{self.user.email} - {self.newsletter.title}"
    
    def mark_as_opened(self):
        """Mark the newsletter as opened by the user."""
        if not self.opened_at:
            self.opened_at = timezone.now()
            self.save()
    
    def mark_as_clicked(self):
        """Mark the newsletter as clicked by the user."""
        self.clicked = True
        self.save()
