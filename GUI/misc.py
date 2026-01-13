import math
import os
import platform
import subprocess
import speak
import sound
from . import chooser, main, tweet, view
import timeline
from application import get_app
from mastodon import MastodonError
try:
	from atproto.exceptions import AtProtocolError, InvokeTimeoutError
except ImportError:
	AtProtocolError = Exception
	InvokeTimeoutError = Exception


def reply(account, status):
	users = account.app.get_users_in_status(account, status)
	NewPost = tweet.TweetGui(account, users + " ", type="reply", status=status)
	NewPost.Show()


def quote(account, status):
	NewPost = tweet.TweetGui(account, type="quote", status=status)
	NewPost.Show()


def user_timeline(account, status):
	u = account.app.get_user_objects_in_status(account, status)
	u2 = []
	for i in u:
		u2.append(i.acct)
	chooser.chooser(account, "User Timeline", "Choose user timeline", u2, "userTimeline")


def user_profile(account, status):
	u = account.app.get_user_objects_in_status(account, status)
	u2 = []
	for i in u:
		u2.append(i.acct)
	chooser.chooser(account, "User Profile", "Choose user profile", u2, "profile")


def url_chooser(account, status):
	title = "Open URL"
	prompt = "Select a URL?"
	type = chooser.ChooseGui.TYPE_URL
	# Get text from status content
	text = account.app.strip_html(getattr(status, 'content', ''))
	urlList = account.app.find_urls_in_text(text)
	if len(urlList) == 1 and account.app.prefs.autoOpenSingleURL:
		account.app.openURL(urlList[0])
	else:
		chooser.chooser(account, title, prompt, urlList, type)


def follow(account, status):
	u = account.app.get_user_objects_in_status(account, status)
	u2 = []
	for i in u:
		u2.append(i.acct)
	chooser.chooser(account, "Follow User", "Follow who?", u2, "follow")


def follow_user(account, username):
	try:
		user = account.follow(username)
		sound.play(account, "follow")
	except (MastodonError, AtProtocolError, InvokeTimeoutError) as error:
		account.app.handle_error(error, "Follow " + username)


def unfollow(account, status):
	u = account.app.get_user_objects_in_status(account, status)
	u2 = []
	for i in u:
		u2.append(i.acct)
	chooser.chooser(account, "Unfollow User", "Unfollow who?", u2, "unfollow")


def unfollow_user(account, username):
	try:
		user = account.unfollow(username)
		sound.play(account, "unfollow")
	except (MastodonError, AtProtocolError, InvokeTimeoutError) as error:
		account.app.handle_error(error, "Unfollow " + username)


def block(account, status):
	u = account.app.get_user_objects_in_status(account, status)
	u2 = []
	for i in u:
		u2.append(i.acct)
	chooser.chooser(account, "Block User", "Block who?", u2, "block")


def unblock(account, status):
	u = account.app.get_user_objects_in_status(account, status)
	u2 = []
	for i in u:
		u2.append(i.acct)
	chooser.chooser(account, "Unblock User", "Unblock who?", u2, "block")


def mute(account, status):
	u = account.app.get_user_objects_in_status(account, status)
	u2 = []
	for i in u:
		u2.append(i.acct)
	chooser.chooser(account, "Mute User", "Mute who?", u2, "mute")


def unmute(account, status):
	u = account.app.get_user_objects_in_status(account, status)
	u2 = []
	for i in u:
		u2.append(i.acct)
	chooser.chooser(account, "Unmute User", "Unmute who?", u2, "unmute")


def add_to_list(account, status):
	u = account.app.get_user_objects_in_status(account, status)
	u2 = []
	for i in u:
		u2.append(i.acct)
	chooser.chooser(account, "Add user to list", "Add who?", u2, "list")


def remove_from_list(account, status):
	u = account.app.get_user_objects_in_status(account, status)
	u2 = []
	for i in u:
		u2.append(i.acct)
	chooser.chooser(account, "Remove user from list", "Remove who?", u2, "listr")


def message(account, status):
	# Direct message - get the user from the status
	user = status.account.acct
	message_user(account, user)


def message_user(account, user):
	NewPost = tweet.TweetGui(account, user, "message")
	NewPost.Show()


def boost(account, status):
	try:
		account.boost(status.id)
		account.app.prefs.boosts_sent += 1
		sound.play(account, "send_boost")
	except (MastodonError, AtProtocolError, InvokeTimeoutError) as error:
		account.app.handle_error(error, "boost")


def favourite(account, status):
	try:
		if getattr(status, 'favourited', False):
			account.unfavourite(status.id)
			status.favourited = False
			sound.play(account, "unlike")
		else:
			account.favourite(status.id)
			account.app.prefs.favourites_sent += 1
			status.favourited = True
			sound.play(account, "like")
	except (MastodonError, AtProtocolError, InvokeTimeoutError) as error:
		account.app.handle_error(error, "favourite post")


def followers(account, id=-1):
	if id == -1:
		id = account.me.id
	flw = view.UserViewGui(account, account.followers(id=id), "Followers")
	flw.Show()


def following(account, id=-1):
	if id == -1:
		id = account.me.id
	flw = view.UserViewGui(account, account.following(id=id), "Following")
	flw.Show()


def mutual_following(account):
	# Mastodon doesn't have a direct mutual following endpoint
	# We'd need to compare followers and following lists
	try:
		followers_list = list(account.api.account_followers(id=account.me.id, limit=80))
		following_list = list(account.api.account_following(id=account.me.id, limit=80))
		follower_ids = {f.id for f in followers_list}
		mutual = [f for f in following_list if f.id in follower_ids]
		flw = view.UserViewGui(account, mutual, "Mutual followers")
		flw.Show()
	except (MastodonError, AtProtocolError, InvokeTimeoutError) as error:
		account.app.handle_error(error, "Get mutual followers")


def not_following_me(account):
	# Find users I follow who don't follow me back
	try:
		followers_list = list(account.api.account_followers(id=account.me.id, limit=80))
		following_list = list(account.api.account_following(id=account.me.id, limit=80))
		follower_ids = {f.id for f in followers_list}
		not_following = [f for f in following_list if f.id not in follower_ids]
		flw = view.UserViewGui(account, not_following, "Users not following me")
		flw.Show()
	except (MastodonError, AtProtocolError, InvokeTimeoutError) as error:
		account.app.handle_error(error, "Get users not following me")


def not_following(account):
	# Find users who follow me that I don't follow back
	try:
		followers_list = list(account.api.account_followers(id=account.me.id, limit=80))
		following_list = list(account.api.account_following(id=account.me.id, limit=80))
		following_ids = {f.id for f in following_list}
		not_following = [f for f in followers_list if f.id not in following_ids]
		flw = view.UserViewGui(account, not_following, "Users I don't follow")
		flw.Show()
	except (MastodonError, AtProtocolError, InvokeTimeoutError) as error:
		account.app.handle_error(error, "Get users I don't follow")


def havent_posted(account):
	# Find users who haven't posted recently
	flw = view.UserViewGui(account, account.havent_posted(), "Users who haven't posted recently")
	flw.Show()


# Alias for backwards compatibility
def havent_tweeted(account):
	havent_posted(account)


def user_timeline_user(account, username, focus=True):
	if username in account.prefs.user_timelines and focus:
		account.app.alert("You already have a timeline for this user open.", "Error")
		return False
	if len(account.prefs.user_timelines) >= 8:
		account.app.alert("You cannot have this many user timelines open! Please consider using a list instead.", "Error")
		return False
	user = account.app.lookup_user_name(account, username)
	if user != -1:
		if not focus:
			account.timelines.append(timeline.timeline(account, name=username + "'s Timeline", type="user", data=username, user=user, silent=True))
		else:
			account.timelines.append(timeline.timeline(account, name=username + "'s Timeline", type="user", data=username, user=user))
		if username not in account.prefs.user_timelines:
			account.prefs.user_timelines.append(username)
		main.window.refreshTimelines()
		if focus:
			account.currentIndex = len(account.timelines) - 1
			main.window.list.SetSelection(len(account.timelines) - 1)
			main.window.on_list_change(None)
		return True


def search(account, q, focus=True):
	if not focus:
		account.timelines.append(timeline.timeline(account, name=q + " Search", type="search", data=q, silent=True))
	else:
		account.timelines.append(timeline.timeline(account, name=q + " Search", type="search", data=q))
	if q not in account.prefs.search_timelines:
		account.prefs.search_timelines.append(q)
	main.window.refreshTimelines()
	if focus:
		account.currentIndex = len(account.timelines) - 1
		main.window.list.SetSelection(len(account.timelines) - 1)
		main.window.on_list_change(None)


def user_search(account, q):
	try:
		result = account.api.account_search(q=q, limit=40)
		users = list(result)
		u = view.UserViewGui(account, users, "User search for " + q)
		u.Show()
	except (MastodonError, AtProtocolError, InvokeTimeoutError) as error:
		account.app.handle_error(error, "User search")


def list_timeline(account, n, q, focus=True):
	# Check if list already open
	for item in account.prefs.list_timelines:
		if item.get('id') == q:
			if focus:
				account.app.alert("You already have a timeline for this list open!", "Error")
			return
	if len(account.prefs.list_timelines) >= 8:
		account.app.alert("You cannot have this many list timelines open!", "Error")
		return
	if not focus:
		account.timelines.append(timeline.timeline(account, name=n + " List", type="list", data=q, silent=True))
	else:
		account.timelines.append(timeline.timeline(account, name=n + " List", type="list", data=q))
	# Save as dict with name for faster restoration (no API call needed)
	account.prefs.list_timelines.append({'id': q, 'name': n})
	main.window.refreshTimelines()
	if focus:
		account.currentIndex = len(account.timelines) - 1
		main.window.list.SetSelection(len(account.timelines) - 1)
		main.window.on_list_change(None)


def next_in_thread(account):
	status = account.currentTimeline.statuses[account.currentTimeline.index]
	if hasattr(status, 'in_reply_to_id') and status.in_reply_to_id is not None:
		newindex = account.app.find_status(account.currentTimeline, status.in_reply_to_id)
		if newindex > -1:
			account.currentTimeline.index = newindex
			main.window.list2.SetSelection(newindex)
	else:
		sound.play(account, "boundary")


def previous_in_thread(account):
	newindex = -1
	newindex = account.app.find_reply(account.currentTimeline, account.currentTimeline.statuses[account.currentTimeline.index].id)
	if newindex > -1:
		account.currentTimeline.index = newindex
		main.window.list2.SetSelection(newindex)
	else:
		sound.play(account, "boundary")


def previous_from_user(account):
	newindex = -1
	oldindex = account.currentTimeline.index
	user = account.currentTimeline.statuses[account.currentTimeline.index].account
	newindex2 = 0
	for i in account.currentTimeline.statuses:
		if newindex2 >= oldindex:
			break
		if i.account.id == user.id:
			newindex = newindex2
		newindex2 += 1

	if newindex > -1:
		account.currentTimeline.index = newindex
		main.window.list2.SetSelection(newindex)
	else:
		sound.play(account, "boundary")


def next_from_user(account):
	newindex = -1
	oldindex = account.currentTimeline.index
	status = account.currentTimeline.statuses[account.currentTimeline.index]
	user = account.currentTimeline.statuses[account.currentTimeline.index].account
	newindex2 = 0
	for i in account.currentTimeline.statuses:
		if i != status and i.account.id == user.id and newindex2 >= oldindex:
			newindex = newindex2
			break
		newindex2 += 1

	if newindex > -1:
		account.currentTimeline.index = newindex
		main.window.list2.SetSelection(newindex)
	else:
		sound.play(account, "boundary")


def delete(account, status):
	try:
		account.api.status_delete(id=status.id)
		account.currentTimeline.statuses.remove(status)
		main.window.list2.Delete(account.currentTimeline.index)
		sound.play(account, "delete")
		main.window.list2.SetSelection(account.currentTimeline.index)
	except (MastodonError, AtProtocolError, InvokeTimeoutError) as error:
		account.app.handle_error(error, "Delete post")


def load_conversation(account, status):
	for i in account.timelines:
		if i.type == "conversation":
			return False
	display_name = getattr(status.account, 'display_name', '') or status.account.acct
	account.timelines.append(timeline.timeline(account, name="Conversation with " + display_name, type="conversation", data=status.account.acct, status=status))
	main.window.refreshTimelines()
	main.window.list.SetSelection(len(account.timelines) - 1)
	account.currentIndex = len(account.timelines) - 1
	main.window.on_list_change(None)


def play(status):
	if sound.player is not None and sound.player.is_playing:
		speak.speak("Stopped")
		sound.stop()
		return
	text = get_app().strip_html(getattr(status, 'content', ''))
	urls = get_app().find_urls_in_text(text)
	try:
		speak.speak("Retrieving URL...")
		audio = sound.get_audio_urls(urls)[0]
		a = audio['func'](audio['url'])
		sound.play_url(a)
	except:
		speak.speak("No audio.")


def play_external(status):
	"""Play audio from a post - checks attachments first, then URLs in text."""
	# If already playing, stop
	if sound.player is not None and sound.player.is_playing:
		speak.speak("Stopped")
		sound.stop()
		return

	audio_url = None

	# First check media attachments for audio
	media_attachments = getattr(status, 'media_attachments', []) or []
	for attachment in media_attachments:
		media_type = getattr(attachment, 'type', '') or ''
		if media_type.lower() == 'audio':
			audio_url = getattr(attachment, 'url', None)
			if audio_url:
				break

	# If no audio attachment, check URLs in text
	if not audio_url:
		text = get_app().strip_html(getattr(status, 'content', ''))
		urls = get_app().find_urls_in_text(text)
		audio_urls = sound.get_audio_urls(urls)
		if audio_urls:
			audio_url = audio_urls[0]['url']

	if audio_url:
		speak.speak("Playing audio...")
		sound.play_url(audio_url)
	else:
		speak.speak("No audio.")
