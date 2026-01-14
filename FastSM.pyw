import time
import threading
import os
import json
_start = time.time()
def _log(msg):
	print(f"[{time.time() - _start:.2f}s] {msg}")

def _has_bluesky_accounts():
	"""Check if any Bluesky accounts are configured (without loading full config module)."""
	# Check for portable mode (userdata folder in current directory)
	userdata_path = os.path.join(os.getcwd(), "userdata")
	if os.path.isdir(userdata_path):
		config_base = userdata_path
		prefix = ""
	else:
		# Normal mode - use APPDATA on Windows
		config_base = os.environ.get("APPDATA", os.path.expanduser("~"))
		prefix = "FastSM/"

	# Check account0, account1, etc. for bluesky platform_type
	for i in range(10):  # Check up to 10 accounts
		config_path = os.path.join(config_base, f"{prefix}account{i}", "config.json")
		if not os.path.exists(config_path):
			continue
		try:
			with open(config_path, 'r') as f:
				data = json.load(f)
				if data.get("platform_type") == "bluesky":
					return True
		except:
			pass
	return False

# Only pre-import atproto if there are Bluesky accounts (takes ~35s)
if _has_bluesky_accounts():
	def _preimport_atproto():
		try:
			import atproto
		except:
			pass
	threading.Thread(target=_preimport_atproto, daemon=True).start()

_log("Starting imports...")
import application
from application import get_app
import platform
import sys
sys.dont_write_bytecode=True
if platform.system()!="Darwin":
	f=open("errors.log","a")
	sys.stderr=f
import shutil
import os
if os.path.exists(os.path.expandvars("%temp%\gen_py")):
	shutil.rmtree(os.path.expandvars("%temp%\gen_py"))
_log("Importing wx...")
import wx
_log("Creating wx.App...")
wx_app = wx.App(redirect=False)

_log("Importing speak...")
import speak
_log("Importing GUI.main (creates window)...")
from GUI import main
_log("Getting app instance...")
fastsm_app = get_app()
_log("Calling app.load()...")
fastsm_app.load()
_log("App loaded, showing window...")
if fastsm_app.prefs.window_shown:
	main.window.Show()
else:
	speak.speak("Welcome to FastSM! Main window hidden.")
_log("Starting main loop")
wx_app.MainLoop()
