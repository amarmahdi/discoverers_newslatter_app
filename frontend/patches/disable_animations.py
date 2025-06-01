"""
Monkey patch to disable all animations in Flet
This patch addresses zoom/transition animations when changing pages
"""

def apply_patches():
    """Apply monkey patches to disable all animations in Flet"""
    import flet as ft
    from flet.core.page import Page
    
    # Store the original update method
    original_update = Page.update
    
    # Override the update method to always disable animations
    def patched_update(self, *args, **kwargs):
        # Force animate to be False regardless of what was passed
        kwargs['animate'] = False
        return original_update(self, *args, **kwargs)
    
    # Apply the patch
    Page.update = patched_update
    
    # Disable all animation-related properties on the Page class
    original_page_init = Page.__init__
    
    def patched_page_init(self, *args, **kwargs):
        # Call the original init
        original_page_init(self, *args, **kwargs)
        
        # Disable all animations
        self.animation = None
        self.route_animation = None
        self.views_transition = None
        
        # Ensure page transitions are disabled
        if hasattr(self, 'theme') and self.theme:
            if not hasattr(self.theme, 'page_transitions'):
                self.theme.page_transitions = ft.PageTransitionsTheme()
            
            # Set all platform transitions to NONE
            self.theme.page_transitions.android = ft.PageTransitionEffect.NONE
            self.theme.page_transitions.ios = ft.PageTransitionEffect.NONE
            self.theme.page_transitions.linux = ft.PageTransitionEffect.NONE
            self.theme.page_transitions.macos = ft.PageTransitionEffect.NONE
            self.theme.page_transitions.windows = ft.PageTransitionEffect.NONE
    
    # Apply the patch
    Page.__init__ = patched_page_init
    
    print("✅ Applied patches to disable all Flet animations")
