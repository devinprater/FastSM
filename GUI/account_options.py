from sound_lib import stream
import platform
import os, sys
import wx
from . import main
from application import get_app

class general(wx.Panel, wx.Dialog):
	def __init__(self, account, parent):
		self.snd = stream.FileStream(file=get_app().confpath+"/sounds/default/boundary.ogg")
		self.account=account
		super(general, self).__init__(parent)
		self.main_box = wx.BoxSizer(wx.VERTICAL)
		self.soundpack_box = wx.BoxSizer(wx.VERTICAL)
		self.soundpacklist_label=wx.StaticText(self, -1, "Soundpacks")
		self.soundpackslist = wx.ListBox(self, -1)
		self.soundpack_box.Add(self.soundpackslist, 0, wx.ALL, 10)
		self.soundpackslist.Bind(wx.EVT_LISTBOX, self.on_soundpacks_list_change)
		dirs = os.listdir(get_app().confpath+"/sounds")
		for i in range(0,len(dirs)):
			if not dirs[i].startswith("_") and not dirs[i].startswith(".DS"):
				self.soundpackslist.Insert(dirs[i],self.soundpackslist.GetCount())
				if account.prefs.soundpack==dirs[i]:
					self.soundpackslist.SetSelection(self.soundpackslist.GetCount()-1)
					self.sp=dirs[i]
		try:
			dirs2 = os.listdir("sounds")
			for i in range(0,len(dirs2)):
				if not dirs2[i].startswith("_") and not dirs2[i].startswith(".DS") and dirs2[i] not in dirs:
					self.soundpackslist.Insert(dirs2[i],self.soundpackslist.GetCount())
					if account.prefs.soundpack==dirs2[i]:
						self.soundpackslist.SetSelection(self.soundpackslist.GetCount()-1)
						self.sp=dirs2[i]
		except:
			pass
		if not hasattr(self,"sp"):
			self.sp="default"
		self.text_label = wx.StaticText(self, -1, "Sound pan")
		self.soundpan = wx.Slider(self, -1, int(self.account.prefs.soundpan*50),-50,50,name="Soundpack Pan")
		self.soundpan.Bind(wx.EVT_SLIDER,self.OnPan)
		self.main_box.Add(self.soundpan, 0, wx.ALL, 10)
		self.text_label = wx.StaticText(self, -1, "Post Footer (Optional)")
		self.footer = wx.TextCtrl(self, -1, "",style=wx.TE_MULTILINE)
		self.main_box.Add(self.footer, 0, wx.ALL, 10)
		self.footer.AppendText(account.prefs.footer)
		# Get max chars from account, default to 500
		max_chars = getattr(account, 'max_chars', 500)
		self.footer.SetMaxLength(max_chars)

		# Mastodon-specific options
		platform_type = getattr(account.prefs, 'platform_type', 'mastodon')
		if platform_type == 'mastodon':
			self.mentions_in_notifications = wx.CheckBox(self, -1, "Show mentions in notifications buffer")
			self.mentions_in_notifications.SetValue(account.prefs.mentions_in_notifications)
			self.main_box.Add(self.mentions_in_notifications, 0, wx.ALL, 10)
		else:
			self.mentions_in_notifications = None

	def OnPan(self,event):
		pan=self.soundpan.GetValue()/50
		self.snd.pan=pan
		self.snd.play()

	def on_soundpacks_list_change(self, event):
		self.sp=event.GetString()

class OptionsGui(wx.Dialog):
	def __init__(self,account):
		self.account=account
		# Use acct for Mastodon instead of screen_name
		acct = getattr(self.account.me, 'acct', 'Unknown')
		wx.Dialog.__init__(self, None, title="Account Options for @" + acct, size=(350,200))
		self.Bind(wx.EVT_CLOSE, self.OnClose)
		self.panel = wx.Panel(self)
		self.main_box = wx.BoxSizer(wx.VERTICAL)
		self.notebook = wx.Notebook(self.panel)
		self.general=general(self.account, self.notebook)
		self.notebook.AddPage(self.general, "General")
		self.main_box.Add(self.notebook, 0, wx.ALL, 10)
		self.ok = wx.Button(self.panel, wx.ID_OK, "&OK")
		self.ok.SetDefault()
		self.ok.Bind(wx.EVT_BUTTON, self.OnOK)
		self.main_box.Add(self.ok, 0, wx.ALL, 10)
		self.close = wx.Button(self.panel, wx.ID_CANCEL, "&Cancel")
		self.close.Bind(wx.EVT_BUTTON, self.OnClose)
		self.main_box.Add(self.close, 0, wx.ALL, 10)
		self.panel.Layout()
		self.general.soundpackslist.SetFocus()

	def OnOK(self, event):
		self.account.prefs.soundpack=self.general.sp
		self.account.prefs.soundpan=self.general.soundpan.GetValue()/50
		self.account.prefs.footer=self.general.footer.GetValue()

		# Handle mentions_in_notifications setting change
		if self.general.mentions_in_notifications is not None:
			old_value = self.account.prefs.mentions_in_notifications
			new_value = self.general.mentions_in_notifications.GetValue()
			if old_value != new_value:
				self.account.prefs.mentions_in_notifications = new_value
				# Clear and reload the notifications timeline
				import threading
				for tl in self.account.timelines:
					if tl.type == "notifications":
						tl.statuses = []
						tl.update_kwargs = {}
						tl.index = 0
						tl.initial = True
						if hasattr(tl, '_unfiltered_statuses'):
							tl._unfiltered_statuses = []
						# Reload in background
						threading.Thread(target=tl.load, daemon=True).start()
						break

		self.general.snd.free()
		self.Destroy()

	def OnClose(self, event):
		self.general.snd.free()
		self.Destroy()
