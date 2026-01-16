"""Theme support for FastSM - dark mode and light mode styling."""

import wx
import sys

# Dark mode colors
DARK_BG = wx.Colour(32, 32, 32)
DARK_FG = wx.Colour(255, 255, 255)
DARK_TEXT_BG = wx.Colour(45, 45, 45)
DARK_BUTTON_BG = wx.Colour(60, 60, 60)

# Light mode colors (system defaults)
LIGHT_BG = wx.NullColour
LIGHT_FG = wx.NullColour


def is_os_dark_mode():
    """Detect if the OS is currently in dark mode."""
    # wxPython 4.1+ has wx.SystemSettings.GetAppearance()
    if hasattr(wx.SystemSettings, 'GetAppearance'):
        try:
            appearance = wx.SystemSettings.GetAppearance()
            if hasattr(appearance, 'IsDark'):
                return appearance.IsDark()
        except:
            pass

    # Fallback: check system colors
    # If the window background is dark, assume dark mode
    try:
        bg = wx.SystemSettings.GetColour(wx.SYS_COLOUR_WINDOW)
        # Calculate luminance - if low, it's dark mode
        luminance = (0.299 * bg.Red() + 0.587 * bg.Green() + 0.114 * bg.Blue()) / 255
        return luminance < 0.5
    except:
        return False


def get_dark_mode_enabled():
    """Check if dark mode is enabled in user preferences."""
    try:
        from application import get_app
        app = get_app()
        if app and hasattr(app, 'prefs'):
            mode = getattr(app.prefs, 'dark_mode', 'off')
            if mode == 'on':
                return True
            elif mode == 'auto':
                return is_os_dark_mode()
    except:
        pass
    return False


def apply_theme(window):
    """Apply the current theme to a window and its children.

    Call this after creating a dialog/frame to apply dark mode if enabled.
    """
    if not get_dark_mode_enabled():
        return

    _apply_dark_theme(window)


def _apply_dark_theme(window):
    """Recursively apply dark theme to a window and its children."""
    try:
        # Set colors on the window itself
        window.SetBackgroundColour(DARK_BG)
        window.SetForegroundColour(DARK_FG)

        # Handle specific widget types
        if isinstance(window, wx.TextCtrl):
            window.SetBackgroundColour(DARK_TEXT_BG)
            window.SetForegroundColour(DARK_FG)
        elif isinstance(window, wx.ListBox) or isinstance(window, wx.ListCtrl):
            window.SetBackgroundColour(DARK_TEXT_BG)
            window.SetForegroundColour(DARK_FG)
        elif isinstance(window, wx.ComboBox) or isinstance(window, wx.Choice):
            window.SetBackgroundColour(DARK_TEXT_BG)
            window.SetForegroundColour(DARK_FG)
        elif isinstance(window, wx.Button):
            window.SetBackgroundColour(DARK_BUTTON_BG)
            window.SetForegroundColour(DARK_FG)
        elif isinstance(window, wx.CheckBox):
            window.SetForegroundColour(DARK_FG)
        elif isinstance(window, wx.RadioButton):
            window.SetForegroundColour(DARK_FG)
        elif isinstance(window, wx.StaticText):
            window.SetForegroundColour(DARK_FG)
        elif isinstance(window, wx.Notebook):
            window.SetBackgroundColour(DARK_BG)
            window.SetForegroundColour(DARK_FG)
        elif isinstance(window, wx.Panel):
            window.SetBackgroundColour(DARK_BG)
            window.SetForegroundColour(DARK_FG)
    except:
        pass  # Some widgets may not support color changes

    # Recursively apply to children
    for child in window.GetChildren():
        _apply_dark_theme(child)

    # Refresh the window
    try:
        window.Refresh()
    except:
        pass
