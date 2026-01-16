from application import get_app
from . import theme
import wx

class ProfileGui(wx.Dialog):

	def __init__(self, account):
		self.account = account
		s = account.api.account_verify_credentials()
		wx.Dialog.__init__(self, None, title="Profile Editor", size=(350, 200))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.panel = wx.Panel(self)
		self.main_box = wx.BoxSizer(wx.VERTICAL)

		self.name_label = wx.StaticText(self.panel, -1, "Display Name")
		self.name = wx.TextCtrl(self.panel, -1, "")
		self.main_box.Add(self.name, 0, wx.ALL, 10)
		self.name.SetFocus()
		display_name = getattr(s, 'display_name', '')
		if display_name:
			self.name.SetValue(display_name)

		self.description_label = wx.StaticText(self.panel, -1, "Bio")
		self.description = wx.TextCtrl(self.panel, -1, "", style=wx.TE_MULTILINE)
		self.main_box.Add(self.description, 0, wx.ALL, 10)
		note = getattr(s, 'note', '')
		if note:
			# Strip HTML from the bio
			self.description.SetValue(self.account.app.strip_html(note))

		# Mastodon profile fields (up to 4 key-value pairs)
		self.fields_label = wx.StaticText(self.panel, -1, "Profile Fields (Name: Value, one per line)")
		self.fields = wx.TextCtrl(self.panel, -1, "", style=wx.TE_MULTILINE)
		self.main_box.Add(self.fields, 0, wx.ALL, 10)
		fields = getattr(s, 'fields', [])
		if fields:
			field_text = ""
			for field in fields:
				name = getattr(field, 'name', '') or field.get('name', '')
				value = getattr(field, 'value', '') or field.get('value', '')
				if name and value:
					field_text += name + ": " + self.account.app.strip_html(value) + "\n"
			self.fields.SetValue(field_text.strip())

		# Locked account option
		self.locked = wx.CheckBox(self.panel, -1, "Lock account (manually approve followers)")
		self.main_box.Add(self.locked, 0, wx.ALL, 10)
		self.locked.SetValue(getattr(s, 'locked', False))

		self.update = wx.Button(self.panel, wx.ID_DEFAULT, "&Update")
		self.update.SetDefault()
		self.update.Bind(wx.EVT_BUTTON, self.Update)
		self.main_box.Add(self.update, 0, wx.ALL, 10)

		self.close = wx.Button(self.panel, wx.ID_CANCEL, "&Cancel")
		self.close.Bind(wx.EVT_BUTTON, self.OnClose)
		self.main_box.Add(self.close, 0, wx.ALL, 10)
		self.panel.Layout()
		theme.apply_theme(self)

	def Update(self, event):
		# Parse fields from text
		fields_list = []
		fields_text = self.fields.GetValue().strip()
		if fields_text:
			for line in fields_text.split("\n"):
				if ": " in line:
					name, value = line.split(": ", 1)
					fields_list.append({"name": name.strip(), "value": value.strip()})

		try:
			self.account.api.account_update_credentials(
				display_name=self.name.GetValue(),
				note=self.description.GetValue(),
				fields=fields_list if fields_list else None,
				locked=self.locked.GetValue()
			)
		except Exception as e:
			self.account.app.handle_error(e, "Update profile")
		self.Destroy()

	def OnClose(self, event):
		self.Destroy()
