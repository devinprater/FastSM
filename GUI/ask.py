import wx

def ask(parent=None, message="", caption="", default_value=""):
	dlg = wx.TextEntryDialog(parent, caption, message, value=default_value)
	result_code = dlg.ShowModal()
	if result_code == wx.ID_OK:
		result = dlg.GetValue()
	else:
		result = None
	dlg.Destroy()
	return result
