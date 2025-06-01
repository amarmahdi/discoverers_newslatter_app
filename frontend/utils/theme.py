import flet as ft

def get_theme():
    """Return a custom theme for the application"""
    return ft.Theme(
        color_scheme_seed=ft.Colors.BLUE,
        use_material3=True,
    )
