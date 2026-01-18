import wx
from . import theme

# Duration options in seconds
DURATION_OPTIONS = [
	("5 minutes", 5 * 60),
	("30 minutes", 30 * 60),
	("1 hour", 60 * 60),
	("6 hours", 6 * 60 * 60),
	("12 hours", 12 * 60 * 60),
	("1 day", 24 * 60 * 60),
	("3 days", 3 * 24 * 60 * 60),
	("7 days", 7 * 24 * 60 * 60),
]

class PollGui(wx.Dialog):
	def __init__(self):
		wx.Dialog.__init__(self, None, title="Create Poll", size=(400, 350))
		self.panel = wx.Panel(self)
		self.main_box = wx.BoxSizer(wx.VERTICAL)

		# Duration dropdown
		duration_label = wx.StaticText(self.panel, -1, "&Duration:")
		self.main_box.Add(duration_label, 0, wx.LEFT | wx.TOP, 10)
		self.duration = wx.Choice(self.panel, -1, choices=[opt[0] for opt in DURATION_OPTIONS], name="Duration")
		self.duration.SetSelection(5)  # Default to 1 day
		self.main_box.Add(self.duration, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		self.duration.SetFocus()

		# Multiple choice checkbox
		self.multiple = wx.CheckBox(self.panel, -1, "&Allow multiple choices")
		self.main_box.Add(self.multiple, 0, wx.ALL, 10)

		# Hide totals checkbox
		self.hide_totals = wx.CheckBox(self.panel, -1, "&Hide results until poll ends")
		self.main_box.Add(self.hide_totals, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)

		# Options
		opt1_label = wx.StaticText(self.panel, -1, "Option &1:")
		self.main_box.Add(opt1_label, 0, wx.LEFT | wx.TOP, 10)
		self.opt1 = wx.TextCtrl(self.panel, -1, "", style=wx.TE_DONTWRAP, name="Option 1")
		self.main_box.Add(self.opt1, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

		opt2_label = wx.StaticText(self.panel, -1, "Option &2:")
		self.main_box.Add(opt2_label, 0, wx.LEFT | wx.TOP, 10)
		self.opt2 = wx.TextCtrl(self.panel, -1, "", style=wx.TE_DONTWRAP, name="Option 2")
		self.main_box.Add(self.opt2, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

		opt3_label = wx.StaticText(self.panel, -1, "Option &3 (optional):")
		self.main_box.Add(opt3_label, 0, wx.LEFT | wx.TOP, 10)
		self.opt3 = wx.TextCtrl(self.panel, -1, "", style=wx.TE_DONTWRAP, name="Option 3")
		self.main_box.Add(self.opt3, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

		opt4_label = wx.StaticText(self.panel, -1, "Option &4 (optional):")
		self.main_box.Add(opt4_label, 0, wx.LEFT | wx.TOP, 10)
		self.opt4 = wx.TextCtrl(self.panel, -1, "", style=wx.TE_DONTWRAP, name="Option 4")
		self.main_box.Add(self.opt4, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)

		# Buttons
		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.ok = wx.Button(self.panel, wx.ID_OK, "&OK")
		self.ok.SetDefault()
		btn_sizer.Add(self.ok, 0, wx.ALL, 5)
		self.close = wx.Button(self.panel, wx.ID_CANCEL, "&Cancel")
		btn_sizer.Add(self.close, 0, wx.ALL, 5)
		self.main_box.Add(btn_sizer, 0, wx.ALIGN_CENTER | wx.ALL, 10)

		self.panel.SetSizer(self.main_box)
		self.panel.Layout()
		theme.apply_theme(self)

	def get_expires_in(self):
		"""Get the selected duration in seconds."""
		selection = self.duration.GetSelection()
		if selection >= 0 and selection < len(DURATION_OPTIONS):
			return DURATION_OPTIONS[selection][1]
		return 24 * 60 * 60  # Default to 1 day

	def get_multiple(self):
		"""Get whether multiple choices are allowed."""
		return self.multiple.GetValue()

	def get_hide_totals(self):
		"""Get whether to hide totals until poll ends."""
		return self.hide_totals.GetValue()

	# Legacy compatibility - runfor property
	@property
	def runfor(self):
		"""Legacy property for backwards compatibility."""
		class RunforWrapper:
			def __init__(self, parent):
				self.parent = parent
			def GetValue(self):
				# Return value that when multiplied by 60*24 gives expires_in
				# Old code does: poll_runfor = p.runfor.GetValue() * 60 * 24
				# Then: expires_in=self.poll_runfor * 60
				# So: expires_in = runfor * 60 * 24 * 60 = runfor * 86400
				# We want expires_in to be get_expires_in(), so:
				# runfor = get_expires_in() / 86400
				return self.parent.get_expires_in() / 86400
		return RunforWrapper(self)
