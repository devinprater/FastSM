import wx
from . import misc, theme, view

class ListsGui(wx.Dialog):
	def __init__(self, account, user=None, add=True):
		self.account = account
		self.add = add
		self.user = user
		# Use Mastodon API for lists
		self.lists = list(self.account.api.lists())
		wx.Dialog.__init__(self, None, title="Lists", size=(350, 200))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.panel = wx.Panel(self)
		self.main_box = wx.BoxSizer(wx.VERTICAL)
		self.list_label = wx.StaticText(self.panel, -1, label="&Lists")
		self.main_box.Add(self.list_label, 0, wx.LEFT | wx.TOP, 10)
		self.list = wx.ListBox(self.panel, -1)
		self.main_box.Add(self.list, 0, wx.EXPAND | wx.ALL, 10)
		self.list.SetFocus()
		self.list.Bind(wx.EVT_LISTBOX, self.on_list_change)
		self.add_items()
		if self.user is not None:
			if self.add:
				self.load = wx.Button(self.panel, wx.ID_DEFAULT, "&Add")
			else:
				self.load = wx.Button(self.panel, wx.ID_DEFAULT, "&Remove")
		else:
			self.load = wx.Button(self.panel, wx.ID_DEFAULT, "&Load list")
		self.load.SetDefault()
		self.load.Bind(wx.EVT_BUTTON, self.Load)
		self.load.Enable(False)
		self.main_box.Add(self.load, 0, wx.ALL, 10)
		if len(self.lists) > 0:
			self.list.SetSelection(0)
			self.on_list_change(None)
		if self.user is None:
			self.new = wx.Button(self.panel, wx.ID_DEFAULT, "&New list")
			self.new.Bind(wx.EVT_BUTTON, self.New)
			self.main_box.Add(self.new, 0, wx.ALL, 10)
			self.edit = wx.Button(self.panel, wx.ID_DEFAULT, "&Edit list")
			self.edit.Bind(wx.EVT_BUTTON, self.Edit)
			self.main_box.Add(self.edit, 0, wx.ALL, 10)
			if len(self.lists) == 0:
				self.edit.Enable(False)
			self.view_members = wx.Button(self.panel, wx.ID_DEFAULT, "&View list members")
			self.view_members.Bind(wx.EVT_BUTTON, self.ViewMembers)
			self.main_box.Add(self.view_members, 0, wx.ALL, 10)
			if len(self.lists) == 0:
				self.view_members.Enable(False)
			self.remove = wx.Button(self.panel, wx.ID_DEFAULT, "&Remove list")
			self.remove.Bind(wx.EVT_BUTTON, self.Remove)
			self.main_box.Add(self.remove, 0, wx.ALL, 10)
			if len(self.lists) == 0:
				self.remove.Enable(False)
		self.close = wx.Button(self.panel, wx.ID_CANCEL, "&Cancel")
		self.close.Bind(wx.EVT_BUTTON, self.OnClose)
		self.main_box.Add(self.close, 0, wx.ALL, 10)
		self.panel.SetSizer(self.main_box)
		self.panel.Layout()
		theme.apply_theme(self)

	def add_items(self):
		for i in self.lists:
			title = getattr(i, 'title', '') or getattr(i, 'name', 'Unknown')
			self.list.Insert(title, self.list.GetCount())
		if len(self.lists) > 0:
			self.list.SetSelection(0)
		else:
			if hasattr(self, "load"):
				self.load.Enable(False)
			if hasattr(self, "edit"):
				self.edit.Enable(False)
			if hasattr(self, "remove"):
				self.remove.Enable(False)

	def on_list_change(self, event):
		self.load.Enable(True)
		if hasattr(self, "edit"):
			self.edit.Enable(True)
		if hasattr(self, "remove"):
			self.remove.Enable(True)
		if hasattr(self, "view_members"):
			self.view_members.Enable(len(self.lists) > 0)

	def New(self, event):
		l = NewListGui(self.account, on_complete=self.refresh_lists)
		l.ShowModal()
		l.Destroy()

	def Edit(self, event):
		l = NewListGui(self.account, self.lists[self.list.GetSelection()], on_complete=self.refresh_lists)
		l.ShowModal()
		l.Destroy()

	def refresh_lists(self):
		"""Refresh the lists from the API."""
		self.lists = list(self.account.api.lists())
		self.list.Clear()
		self.add_items()
		# Update button states
		if len(self.lists) > 0:
			self.list.SetSelection(0)
			self.on_list_change(None)
		else:
			self.load.Enable(False)
			if hasattr(self, "edit"):
				self.edit.Enable(False)
			if hasattr(self, "remove"):
				self.remove.Enable(False)
			if hasattr(self, "view_members"):
				self.view_members.Enable(False)

	def Remove(self, event):
		selected_list = self.lists[self.list.GetSelection()]
		self.account.api.list_delete(id=selected_list.id)
		self.lists.remove(selected_list)
		self.list.Clear()
		self.add_items()

	def ViewMembers(self, event):
		import speak
		selection = self.list.GetSelection()
		if selection < 0 or selection >= len(self.lists):
			speak.speak("No list selected")
			return
		selected_list = self.lists[selection]
		try:
			members = list(self.account.api.list_accounts(id=selected_list.id))
		except Exception as e:
			speak.speak(f"Error getting list members: {e}")
			return
		if not members:
			speak.speak("This list has no members")
			return
		v = view.UserViewGui(self.account, members, "List members")
		v.ShowModal()

	def Load(self, event):
		import speak
		if self.user is None:
			selected_list = self.lists[self.list.GetSelection()]
			title = getattr(selected_list, 'title', '') or getattr(selected_list, 'name', 'List')
			misc.list_timeline(self.account, title, selected_list.id)
		else:
			selected_list = self.lists[self.list.GetSelection()]
			list_title = getattr(selected_list, 'title', '') or getattr(selected_list, 'name', 'List')
			try:
				if self.add:
					self.account.api.list_accounts_add(id=selected_list.id, account_ids=[self.user.id])
					speak.speak(f"Added to {list_title}")
				else:
					self.account.api.list_accounts_delete(id=selected_list.id, account_ids=[self.user.id])
					speak.speak(f"Removed from {list_title}")
			except Exception as e:
				speak.speak(f"Failed: {str(e)}")
				return  # Don't close dialog on error
		self.Destroy()

	def OnClose(self, event):
		self.Destroy()


class NewListGui(wx.Dialog):
	def __init__(self, account, list_obj=None, on_complete=None):
		self.account = account
		self.list_obj = list_obj
		self.on_complete = on_complete
		title = "New list"
		if list_obj is not None:
			list_title = getattr(list_obj, 'title', '') or getattr(list_obj, 'name', 'List')
			title = "Edit list " + list_title
		wx.Dialog.__init__(self, None, title=title, size=(350, 200))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.panel = wx.Panel(self)
		self.main_box = wx.BoxSizer(wx.VERTICAL)
		self.text_label = wx.StaticText(self.panel, -1, "Name of list")
		self.main_box.Add(self.text_label, 0, wx.LEFT | wx.TOP, 10)
		self.text = wx.TextCtrl(self.panel, -1, "", style=wx.TE_PROCESS_ENTER | wx.TE_DONTWRAP)
		self.main_box.Add(self.text, 0, wx.EXPAND | wx.ALL, 10)
		self.text.SetFocus()
		if list_obj is not None:
			list_title = getattr(list_obj, 'title', '') or getattr(list_obj, 'name', '')
			self.text.SetValue(list_title)

		# Mastodon list replies_policy
		self.replies_label = wx.StaticText(self.panel, -1, "Show replies to")
		self.main_box.Add(self.replies_label, 0, wx.LEFT | wx.TOP, 10)
		self.replies = wx.ComboBox(self.panel, -1, "", style=wx.CB_READONLY)
		self.replies.Insert("No one", 0)  # none
		self.replies.Insert("List members only", 1)  # list
		self.replies.Insert("People you follow", 2)  # followed
		self.replies.SetSelection(1)  # default to list
		if self.list_obj is not None:
			policy = getattr(self.list_obj, 'replies_policy', 'list')
			policy_map = {'none': 0, 'list': 1, 'followed': 2}
			self.replies.SetSelection(policy_map.get(policy, 1))
		self.main_box.Add(self.replies, 0, wx.ALL, 10)

		# Mastodon exclusive setting (hide list members from home timeline)
		self.exclusive = wx.CheckBox(self.panel, -1, "&Hide list members from home timeline")
		if self.list_obj is not None:
			self.exclusive.SetValue(getattr(self.list_obj, 'exclusive', False))
		self.main_box.Add(self.exclusive, 0, wx.ALL, 10)

		if self.list_obj is not None:
			self.create = wx.Button(self.panel, wx.ID_DEFAULT, "&Edit list")
		else:
			self.create = wx.Button(self.panel, wx.ID_DEFAULT, "&Create list")
		self.create.SetDefault()
		self.create.Bind(wx.EVT_BUTTON, self.Create)
		self.main_box.Add(self.create, 0, wx.ALL, 10)
		self.close = wx.Button(self.panel, wx.ID_CANCEL, "&Cancel")
		self.close.Bind(wx.EVT_BUTTON, self.OnClose)
		self.main_box.Add(self.close, 0, wx.ALL, 10)
		self.panel.SetSizer(self.main_box)
		self.panel.Layout()

	def Create(self, event):
		import speak
		replies_map = {0: 'none', 1: 'list', 2: 'followed'}
		replies_policy = replies_map.get(self.replies.GetSelection(), 'list')
		exclusive = self.exclusive.GetValue()

		try:
			if self.list_obj is None:
				self.account.api.list_create(
					title=self.text.GetValue(),
					replies_policy=replies_policy,
					exclusive=exclusive
				)
				speak.speak("List created")
			else:
				self.account.api.list_update(
					id=self.list_obj.id,
					title=self.text.GetValue(),
					replies_policy=replies_policy,
					exclusive=exclusive
				)
				speak.speak("List updated")
			if self.on_complete:
				self.on_complete()
			self.EndModal(wx.ID_OK)
		except Exception as e:
			speak.speak(f"Failed: {str(e)}")

	def OnClose(self, event):
		self.EndModal(wx.ID_CANCEL)
