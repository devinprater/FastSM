"""Dialog for filtering timeline posts by type."""

import wx
from application import get_app


class TimelineFilterDialog(wx.Dialog):
    """Dialog for filtering the current timeline by post type."""

    def __init__(self, parent, timeline):
        wx.Dialog.__init__(self, parent, title="Filter Timeline", size=(400, 350))
        self.timeline = timeline
        self.app = get_app()

        # Store original statuses if not already stored
        if not hasattr(timeline, '_unfiltered_statuses'):
            timeline._unfiltered_statuses = list(timeline.statuses)

        panel = wx.Panel(self)
        main_box = wx.BoxSizer(wx.VERTICAL)

        # Instructions
        label = wx.StaticText(panel, -1, "Check the types of posts you want to show:")
        main_box.Add(label, 0, wx.ALL, 10)

        # Checkboxes for filter options
        self.show_original = wx.CheckBox(panel, -1, "Original posts (not replies or boosts)")
        self.show_original.SetValue(True)
        main_box.Add(self.show_original, 0, wx.ALL, 5)

        self.show_replies = wx.CheckBox(panel, -1, "Replies to others")
        self.show_replies.SetValue(True)
        main_box.Add(self.show_replies, 0, wx.ALL, 5)

        self.show_threads = wx.CheckBox(panel, -1, "Threads (self-replies)")
        self.show_threads.SetValue(True)
        main_box.Add(self.show_threads, 0, wx.ALL, 5)

        self.show_boosts = wx.CheckBox(panel, -1, "Boosts/Reposts")
        self.show_boosts.SetValue(True)
        main_box.Add(self.show_boosts, 0, wx.ALL, 5)

        self.show_quotes = wx.CheckBox(panel, -1, "Quote posts")
        self.show_quotes.SetValue(True)
        main_box.Add(self.show_quotes, 0, wx.ALL, 5)

        self.show_media = wx.CheckBox(panel, -1, "Posts with media")
        self.show_media.SetValue(True)
        main_box.Add(self.show_media, 0, wx.ALL, 5)

        self.show_no_media = wx.CheckBox(panel, -1, "Posts without media")
        self.show_no_media.SetValue(True)
        main_box.Add(self.show_no_media, 0, wx.ALL, 5)

        # Load existing filter settings if present
        if hasattr(timeline, '_filter_settings'):
            settings = timeline._filter_settings
            self.show_original.SetValue(settings.get('original', True))
            self.show_replies.SetValue(settings.get('replies', True))
            self.show_threads.SetValue(settings.get('threads', True))
            self.show_boosts.SetValue(settings.get('boosts', True))
            self.show_quotes.SetValue(settings.get('quotes', True))
            self.show_media.SetValue(settings.get('media', True))
            self.show_no_media.SetValue(settings.get('no_media', True))

        # Buttons
        button_box = wx.BoxSizer(wx.HORIZONTAL)

        self.ok_btn = wx.Button(panel, wx.ID_OK, "&Apply")
        self.ok_btn.Bind(wx.EVT_BUTTON, self.on_apply)
        button_box.Add(self.ok_btn, 0, wx.ALL, 5)

        self.clear_btn = wx.Button(panel, -1, "&Clear Filter")
        self.clear_btn.Bind(wx.EVT_BUTTON, self.on_clear)
        button_box.Add(self.clear_btn, 0, wx.ALL, 5)

        self.cancel_btn = wx.Button(panel, wx.ID_CANCEL, "&Cancel")
        button_box.Add(self.cancel_btn, 0, wx.ALL, 5)

        main_box.Add(button_box, 0, wx.ALL | wx.ALIGN_CENTER, 10)

        panel.SetSizer(main_box)
        panel.Layout()

    def _get_post_for_check(self, status):
        """Get the actual post to check (unwrap boosts for content checks)."""
        if hasattr(status, 'reblog') and status.reblog:
            return status.reblog
        return status

    def _is_boost(self, status):
        """Check if status is a boost/repost."""
        return hasattr(status, 'reblog') and status.reblog is not None

    def _is_quote(self, status):
        """Check if status is a quote post."""
        post = self._get_post_for_check(status)
        return hasattr(post, 'quote') and post.quote is not None

    def _is_reply(self, status):
        """Check if status is a reply to someone else."""
        post = self._get_post_for_check(status)
        if not hasattr(post, 'in_reply_to_id') or post.in_reply_to_id is None:
            return False
        # Check if it's a self-reply (thread) or reply to others
        # For self-reply detection, we need to check if replying to own post
        return not self._is_thread(status)

    def _is_thread(self, status):
        """Check if status is a self-reply (thread continuation)."""
        post = self._get_post_for_check(status)
        if not hasattr(post, 'in_reply_to_id') or post.in_reply_to_id is None:
            return False

        # Get author of this post
        post_author = getattr(post, 'account', None)
        if not post_author:
            return False
        post_acct = getattr(post_author, 'acct', '') or getattr(post_author, 'id', '')

        # Try to find parent post to check author
        parent = self.app.lookup_status(self.app.currentAccount, post.in_reply_to_id)
        if parent:
            parent_author = getattr(parent, 'account', None)
            if parent_author:
                parent_acct = getattr(parent_author, 'acct', '') or getattr(parent_author, 'id', '')
                return post_acct.lower() == parent_acct.lower()

        # If we can't find parent, check if text starts with own handle (common pattern)
        return False

    def _has_media(self, status):
        """Check if status has media attachments."""
        post = self._get_post_for_check(status)
        attachments = getattr(post, 'media_attachments', None)
        return attachments is not None and len(attachments) > 0

    def _is_original(self, status):
        """Check if status is an original post (not reply, not boost)."""
        if self._is_boost(status):
            return False
        post = self._get_post_for_check(status)
        return not hasattr(post, 'in_reply_to_id') or post.in_reply_to_id is None

    def on_apply(self, event):
        """Apply the filter to the timeline."""
        from . import main as main_window

        # Save filter settings
        self.timeline._filter_settings = {
            'original': self.show_original.GetValue(),
            'replies': self.show_replies.GetValue(),
            'threads': self.show_threads.GetValue(),
            'boosts': self.show_boosts.GetValue(),
            'quotes': self.show_quotes.GetValue(),
            'media': self.show_media.GetValue(),
            'no_media': self.show_no_media.GetValue(),
        }

        # Filter statuses
        filtered = []
        for status in self.timeline._unfiltered_statuses:
            if self._should_show(status):
                filtered.append(status)

        self.timeline.statuses = filtered
        self.timeline._is_filtered = True

        # Refresh the list
        main_window.window.refreshList()

        self.Destroy()

    def _should_show(self, status):
        """Determine if a status should be shown based on filter settings."""
        is_boost = self._is_boost(status)
        is_quote = self._is_quote(status)
        is_thread = self._is_thread(status)
        is_reply = self._is_reply(status)
        is_original = self._is_original(status)
        has_media = self._has_media(status)

        # Check boost filter
        if is_boost and not self.show_boosts.GetValue():
            return False

        # Check quote filter
        if is_quote and not self.show_quotes.GetValue():
            return False

        # Check thread filter (self-replies)
        if is_thread and not self.show_threads.GetValue():
            return False

        # Check reply filter (replies to others)
        if is_reply and not self.show_replies.GetValue():
            return False

        # Check original post filter
        if is_original and not is_boost and not self.show_original.GetValue():
            return False

        # Check media filters
        if has_media and not self.show_media.GetValue():
            return False
        if not has_media and not self.show_no_media.GetValue():
            return False

        return True

    def on_clear(self, event):
        """Clear the filter and restore all posts."""
        from . import main as main_window

        if hasattr(self.timeline, '_unfiltered_statuses'):
            self.timeline.statuses = list(self.timeline._unfiltered_statuses)
            self.timeline._is_filtered = False
            if hasattr(self.timeline, '_filter_settings'):
                del self.timeline._filter_settings

        main_window.window.refreshList()
        self.Destroy()


def show_filter_dialog(account):
    """Show the timeline filter dialog for the current timeline."""
    from . import main as main_window
    timeline = account.currentTimeline
    if not timeline:
        return

    dlg = TimelineFilterDialog(main_window.window, timeline)
    dlg.ShowModal()
