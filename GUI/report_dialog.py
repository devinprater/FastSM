"""Report dialog for reporting users and posts."""

import wx
import speak
import sound
from application import get_app


# Report categories that work for both Mastodon and Bluesky
REPORT_CATEGORIES = [
    ("spam", "Spam", "Unwanted commercial content, misleading links, or repetitive posts"),
    ("violation", "Rule Violation", "Violates server or platform rules"),
    ("other", "Other", "Other reason not listed above"),
]

# Mastodon-specific category
MASTODON_CATEGORIES = [
    ("legal", "Legal Issue", "Content that may be illegal in your jurisdiction"),
]


class ReportDialog(wx.Dialog):
    """Dialog for reporting a user or post."""

    def __init__(self, account, user=None, status=None, parent=None):
        """Initialize report dialog.

        Args:
            account: The current account
            user: The user being reported (required)
            status: Optional status providing context (for post reports)
            parent: Parent window
        """
        self.account = account
        self.user = user
        self.status = status
        self.platform_type = getattr(account.prefs, 'platform_type', 'mastodon')
        self.server_rules = []  # Will be populated for Mastodon
        self.thread_statuses = []  # Will hold thread posts if available
        self.selected_status_ids = []  # IDs of selected posts to include

        # Determine what we're reporting
        if status:
            title = f"Report Post by @{user.acct}"
        else:
            title = f"Report @{user.acct}"

        wx.Dialog.__init__(self, parent, title=title, size=(500, 500))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

        self.panel = wx.Panel(self)
        self.main_box = wx.BoxSizer(wx.VERTICAL)

        # Category selection
        cat_label = wx.StaticText(self.panel, -1, "&Category:")
        self.main_box.Add(cat_label, 0, wx.LEFT | wx.TOP, 10)

        # Build category list based on platform
        self.categories = list(REPORT_CATEGORIES)
        if self.platform_type == 'mastodon':
            # Insert legal before other
            self.categories.insert(2, MASTODON_CATEGORIES[0])

        category_choices = [f"{cat[1]} - {cat[2]}" for cat in self.categories]
        self.category = wx.Choice(self.panel, -1, choices=category_choices)
        self.category.SetSelection(0)
        self.category.Bind(wx.EVT_CHOICE, self.OnCategoryChange)
        self.main_box.Add(self.category, 0, wx.EXPAND | wx.ALL, 10)

        # Rules section (Mastodon only, shown when "Rule Violation" selected)
        if self.platform_type == 'mastodon':
            self.rules_label = wx.StaticText(self.panel, -1, "&Rules violated:")
            self.main_box.Add(self.rules_label, 0, wx.LEFT | wx.TOP, 10)
            self.rules_label.Hide()

            self.rules_list = wx.CheckListBox(self.panel, -1, size=(450, 120))
            self.main_box.Add(self.rules_list, 0, wx.EXPAND | wx.ALL, 10)
            self.rules_list.Hide()

            # Fetch server rules in background
            self._fetch_server_rules()
        else:
            self.rules_label = None
            self.rules_list = None

        # Thread posts section (shown if status is part of a thread)
        if status and self.platform_type == 'mastodon':
            self.posts_label = wx.StaticText(self.panel, -1, "&Posts to include in report:")
            self.main_box.Add(self.posts_label, 0, wx.LEFT | wx.TOP, 10)

            self.posts_list = wx.CheckListBox(self.panel, -1, size=(450, 100))
            self.main_box.Add(self.posts_list, 0, wx.EXPAND | wx.ALL, 10)

            # Add the current post first
            self._add_post_to_list(status, check=True)

            # Fetch thread context
            self._fetch_thread_context()
        else:
            self.posts_label = None
            self.posts_list = None

        # Comment/reason
        comment_label = wx.StaticText(self.panel, -1, "&Additional details (optional):")
        self.main_box.Add(comment_label, 0, wx.LEFT | wx.TOP, 10)

        self.comment = wx.TextCtrl(self.panel, -1, style=wx.TE_MULTILINE, size=(450, 80))
        self.main_box.Add(self.comment, 0, wx.EXPAND | wx.ALL, 10)

        # Forward to remote server option (Mastodon only)
        if self.platform_type == 'mastodon':
            # Check if user is from a remote server
            user_domain = user.acct.split('@')[-1] if '@' in user.acct else None
            if user_domain:
                self.forward = wx.CheckBox(self.panel, -1, f"&Forward report to {user_domain}")
                self.forward.SetValue(True)
                self.main_box.Add(self.forward, 0, wx.LEFT | wx.TOP, 10)
            else:
                self.forward = None
        else:
            self.forward = None

        # Info text
        if status:
            info = "This will report the post(s) and author to the moderation team."
        else:
            info = "This will report the user to the moderation team."

        info_text = wx.StaticText(self.panel, -1, info)
        self.main_box.Add(info_text, 0, wx.ALL, 10)

        # Buttons
        btn_sizer = wx.BoxSizer(wx.HORIZONTAL)

        self.submit_btn = wx.Button(self.panel, -1, "&Submit Report")
        self.submit_btn.Bind(wx.EVT_BUTTON, self.OnSubmit)
        btn_sizer.Add(self.submit_btn, 0, wx.ALL, 5)

        self.cancel_btn = wx.Button(self.panel, wx.ID_CANCEL, "&Cancel")
        self.cancel_btn.Bind(wx.EVT_BUTTON, self.OnClose)
        btn_sizer.Add(self.cancel_btn, 0, wx.ALL, 5)

        self.main_box.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)

        self.panel.SetSizer(self.main_box)
        self.category.SetFocus()

    def _fetch_server_rules(self):
        """Fetch server rules from Mastodon instance."""
        try:
            # Get instance info which includes rules
            instance = self.account.api.instance()
            if hasattr(instance, 'rules') and instance.rules:
                self.server_rules = instance.rules
                for rule in self.server_rules:
                    rule_text = getattr(rule, 'text', str(rule))
                    self.rules_list.Append(rule_text)
        except Exception as e:
            # Rules not available - that's okay, some servers don't have them
            pass

    def _fetch_thread_context(self):
        """Fetch thread context to allow selecting multiple posts."""
        if not self.status:
            return

        try:
            # Get the status context (ancestors and descendants)
            status_id = self.status.id
            # Handle reblog - get the original post's context
            if hasattr(self.status, 'reblog') and self.status.reblog:
                status_id = self.status.reblog.id

            context = self.account.api.status_context(id=status_id)

            # Add ancestors (posts before this one in the thread)
            if hasattr(context, 'ancestors') and context.ancestors:
                for post in context.ancestors:
                    # Only include posts by the same user being reported
                    if str(post.account.id) == str(self.user.id):
                        self._add_post_to_list(post, check=False)

            # Add descendants (replies after this post)
            if hasattr(context, 'descendants') and context.descendants:
                for post in context.descendants:
                    # Only include posts by the same user being reported
                    if str(post.account.id) == str(self.user.id):
                        self._add_post_to_list(post, check=False)

        except Exception as e:
            # Context not available - that's okay
            pass

    def _add_post_to_list(self, status, check=False):
        """Add a post to the posts list."""
        if not self.posts_list:
            return

        # Check if already added
        status_id = str(status.id)
        if status_id in [str(s.id) for s in self.thread_statuses]:
            return

        self.thread_statuses.append(status)

        # Create display text
        content = getattr(status, 'content', '') or getattr(status, 'text', '')
        # Strip HTML if present
        content = self.account.app.strip_html(content)
        # Truncate for display
        if len(content) > 80:
            content = content[:80] + "..."
        # Add timestamp
        created = getattr(status, 'created_at', None)
        if created:
            try:
                time_str = self.account.app.parse_date(created)
                display = f"{content} ({time_str})"
            except:
                display = content
        else:
            display = content

        idx = self.posts_list.Append(display)
        if check:
            self.posts_list.Check(idx, True)

    def OnCategoryChange(self, event):
        """Handle category selection change."""
        category_index = self.category.GetSelection()
        category = self.categories[category_index][0]

        # Show/hide rules list based on category
        if self.rules_list and self.rules_label:
            if category == 'violation' and len(self.server_rules) > 0:
                self.rules_label.Show()
                self.rules_list.Show()
            else:
                self.rules_label.Hide()
                self.rules_list.Hide()

            self.panel.Layout()

    def OnSubmit(self, event):
        """Submit the report."""
        category_index = self.category.GetSelection()
        category = self.categories[category_index][0]
        comment = self.comment.GetValue().strip()
        forward = self.forward.GetValue() if self.forward else False

        # Collect selected rule IDs
        rule_ids = []
        if self.rules_list and category == 'violation':
            for i in range(self.rules_list.GetCount()):
                if self.rules_list.IsChecked(i):
                    if i < len(self.server_rules):
                        rule = self.server_rules[i]
                        rule_id = getattr(rule, 'id', None)
                        if rule_id:
                            rule_ids.append(rule_id)

        # Collect selected status IDs
        status_ids = []
        if self.posts_list:
            for i in range(self.posts_list.GetCount()):
                if self.posts_list.IsChecked(i):
                    if i < len(self.thread_statuses):
                        status_ids.append(self.thread_statuses[i].id)
        elif self.status:
            # No posts list, but we have a status - include it
            status_ids = [self.status.id]

        try:
            if self.platform_type == 'bluesky':
                # Bluesky reporting
                if hasattr(self.account, '_platform') and self.account._platform:
                    self.account._platform.report(
                        user_id=self.user.id,
                        status_id=self.status.id if self.status else None,
                        category=category,
                        comment=comment
                    )
            else:
                # Mastodon reporting
                report_kwargs = {
                    'account_id': self.user.id,
                    'comment': comment,
                    'forward': forward,
                    'category': category,
                }

                if status_ids:
                    report_kwargs['status_ids'] = status_ids

                if rule_ids and category == 'violation':
                    report_kwargs['rule_ids'] = rule_ids

                self.account.api.report(**report_kwargs)

            sound.play(self.account, "send")
            report_count = len(status_ids) if status_ids else 0
            if report_count > 1:
                speak.speak(f"Report submitted with {report_count} posts")
            else:
                speak.speak("Report submitted")
            self.EndModal(wx.ID_OK)

        except Exception as e:
            self.account.app.handle_error(e, "Submit report")

    def OnClose(self, event):
        """Close the dialog."""
        self.EndModal(wx.ID_CANCEL)


def report_user(account, user, parent=None):
    """Show report dialog for a user.

    Args:
        account: The current account
        user: The user to report
        parent: Parent window
    """
    dlg = ReportDialog(account, user=user, parent=parent)
    dlg.ShowModal()
    dlg.Destroy()


def report_status(account, status, parent=None):
    """Show report dialog for a status/post.

    Args:
        account: The current account
        status: The status to report
        parent: Parent window
    """
    # Get the user from the status
    user = status.account if hasattr(status, 'account') else None
    if not user:
        speak.speak("Cannot report: no user information available")
        return

    dlg = ReportDialog(account, user=user, status=status, parent=parent)
    dlg.ShowModal()
    dlg.Destroy()
