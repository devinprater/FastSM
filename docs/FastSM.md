# FastSM

Welcome to FastSM!

## What is FastSM?

FastSM is a fully accessible, easy-to-use, light-weight Mastodon/BlueSky client, based off of the old Quinter App from me and Quin created back in 2021. It works on both Windows and Mac, and is open sourced, allowing anyone to contribute if they so wish!

## Interfaces

FastSM has two interfaces. GUI and invisible. Invisible allows you to control FastSM from anywhere on your computer. This is disabled by default, but can be easily enabled in settings. GUI allows you to control FastSM like any other application, with buttons, lists, menus, etc.

## Main window.

The main window of FastSM is simple, allowing anyone (no matter their skill level), to use the application without any issues. It contains two list boxes. One contains all your different timelines (e.g. Home, Mentions, Messages, Likes, etc.), and the other contains all the posts/messages in that particular timeline.

FastSM also has a standard menu bar, allowing you to carry out many functions right from the menu, without having to remember keys! The menus are as follows.

* Application: Various application related functions, such as options, update profile, and exit.
* Actions: This menu contains various different actions, such as post, reply, repost, like, send direct message, etc.
* Users: This menu contains options that let you see mutual follows, people you follow that don't follow you, and vice versa.
* Timeline: The timeline menu let's you control your currently focused timeline. Refreshing it, getting older items, hiding it, etc.
* Audio: The audio menu let's you handle FastSM's audio. It let's you play audio, and adjust the volume of the application.
* Navigation: This menu let's you navigate timelines in advanced ways (e.g. jumping to the next and previous post from a user).
* Help: This is your standard help menu. You can view this document, view stats for nerds, and a lot more!

## Keys.

### GUI

You can find out what keys perform what actions by reading through all of the menu options. For example. Reply (Control+R) or command+r on mac.

### Invisible: 

Here are the default keys for the invisible interface on Windows only, as it does not work on Mac. These keys can be easily remapped by editing keymap.keymap.

* Control+Windows+W: Show or hide the window.
* Alt+Windows+N: Send a post.
* Alt+Windows+left arrow: Previous timeline
* Alt+Windows+right Arrow: Next Timeline.
* Alt+Windows+Up Arrow: Previous Buffer item.
* Alt+Windows+Down Arrow: Next buffer item.
* Control+Windows+r: Reply to a post.
* Control+Windows+Shift+r: Send a repost.
* Alt+Windows+L: Like or unlike (Bluesky), favorite/unfavorite (Mastodon) a post.
* Alt+Windows+Q: Quote a post.
* Alt+Windows+Control+D: Send a direct message.
* Alt+Windows+C: Open a conversation.
* Alt+Windows+V: Open the Post Viewer
* Alt+Windows+Control+Up Arrow: Increase volume.
* Alt+Windows+Control+Down Arrow: Turn down the volume.
* Alt+Windows+Enter: Open a URL
* shift+windows+alt+enter: Play audio in post.
* Alt+Windows+Semi Colon: Speak a brief profile overview.
* Alt+Windows+Shift+Semi Colon: Speak what a post is in reply to.
* Alt+Windows+Page Up: Load previous items.
* Alt+Windows+U: Open a user's timeline
* Alt+Windows+Shift+U: Open a user's profile.
* Alt+Windows+Tick: Destroy a timeline.
* Alt+Windows+Control+U: Refresh.
* Alt+Windows+Home: Go to the top of the buffer.
* Alt+Windows+End: Go to the end of the buffer.
* Alt+Windows+Delete: Delete a post.
* Alt+Windows+Shift+Q: Exit the program.
* Alt+Windows+Left Bracket: View followers.
* Alt+Windows+Right bracket: View Friends.
* alt+windows+o: Options
* control+alt+windows+o: account Options
* alt+windows+shift+left: previous post from same user
* alt+windows+shift+right: next post from same user
* alt+windows+shift+up: previous post in thread
* alt+windows+shift+down: next post in thread
* Control+Windows+Shift+C: Copy the focused post to the clipboard.
* alt+windows+a: Add user to a list
* alt+windows+shift+a: Remove user from a list.
* alt+windows+control+l: View your lists.
* alt+windows+slash: Perform a search.
* Control+Windows+A: Open the account manager.
* Alt+windows+space: Repeat currently focused item.
* Alt+windows+control+a: Speak the current account.
* alt + windows + control + shift + enter: open URL to post in browser.
* alt + windows + e: Toggle autoread for current timeline.
* alt + windows + M: Toggle mute for current timeline.
* Control+Windows+Page up: Move up 20 items.
* Control+Windows+Page down: Move down 20 items.

## Templates.

FastSM supports a template system, allowing you to choose what information you want shown when viewing posts, direct mentions, reposts, etc. Each bit of information goes between two dollar signs ($), and you can have other symbols outside of the dollar signs. The possible objects are as follows: 

### posts: , reposts, and quotes.

* user.screen_name: The @HANDLE of the user.
* user.name: The display name of the user.
* text: The text of the post.
* created_at: The timestamp of when the item was created.
* source: The client it was sent from.
* repost_count: The number of reposts.
* favorite_count: The likes count
* possibly_sensitive: Is this post marked as possibly containing sensative content?
* lang: The language of the post

### Direct Messages: 

* sender.screen_name: The @HANDLE of the user that sent the message.
* sender.name: The display name of the user that sent the message.
* recipient.screen_name: The @HANDLE of the user the message was sent to.
* recipient.name: The display name of the user that received the message.
* text: The text of the message.
* created_at: The timestamp of when the item was created.

### Users

* name: The display name of the user.
* screen_name: the @HANDLE of the user
* followers_count: The amount of followers the user has.
* friends_count: The number of friends the user has.
* statuses_count: The number of posts sent by the user.
* description: The user's bio.

## Options

FastSM has two different options dialogs. One is for global settings that apply across the hole app. The other is for the currently selected account.

### Global options

This dialog is divided into multiple tabs. They are as follows.

* General: General options, such as ask before dismissing timelines.
* Templates: Template settings.
* Advanced: Options that are exparamental, or could possibly break the app if not used propperly.

#### General

* Ask before dismissing timelines: If checked, this will show a warning message when destroying timelines.
* Play a sound when a post contains audio that is playable by either the client or an external media player: If checked, this option will make FastSM make a sound if you come across a post with playable media.
* Play a sound when you navigate to a timeline that may have new items: This option will play a sound if a timeline you navigate to has items that might be new (i.e. you're not at the edge of the timeline).
* Remove emojis and other unicode characters from display names: Tired of people with 50 emojis in their names? Check this box, and suffer no more! If the user in questoin has only emojis, the screen name will show instead.
* Remove emojis and other unicode characters from post text: This option is similar to the username one, but it works with post text.
* Reverse timelines (newest on bottom): This option puts the newest posts at the bottom, rather than at the top.
* Word wrap in text fields: If checked, long lines will wrap onto new lines in any text field, including the new post dialog.
* when getting URLs from a post, automatically open the first URL if it is the only one : If a post contains only one URL, pressing the open URL command will open it by default if this is checked.

#### templates.

* post template: Customizehow standard posts and replies are displayed.
* Quote template: Customize how quotes are displayed.
* Repost template: Customize how your reposts are shown.
* Copy template: Customize what data gets coppied when you copy a post to your clipboard.
* Direct message template: Customize how your DM's are shown.
* User template: Customize what info is shown in user summaries.

#### Advanced

* Enable invisible interface (exparimental): Enables the global hotkeys.
* Sync invisible interface with UI (uncheck for reduced lag in invisible interface): If unchecked, this optoin aims to way improve performance in the invisible interface.
* Repeat items at edges of invisible interface: If this is checked, when you hit an edge in the invisible interface, it will repeat.
* Speak position information when navigating between timelines of invisible interface and switching timelines: If checked, you will be told how far down a timeline you are when navigating to it.
* Update time (in minutes): This changes how frequently the API tries to pull for new posts.
* Max API calls when fetching users in user viewer: This changes how many followers and friends you can pull when viewing them. One request = 200 followers/friends.
* Number of posts to fetch per call (Maximum is 200): Changes how many posts you pull per request (mainly noticeable on startup).
* Enable streaming for home, mentions, and list timelines (This is very experimental! Requires restart to disable): Enables very, very exparamental and breaky streaming API support.

### Account options.

This dialog doesn't currently contain much, and currently only contains the following tabs:

* General: General options.

#### General.

* Soundpacks: Let's you choose your soundpack.
* Sound pan: This allows you to pan account-specific sounds to a different position in the stereo field, so you don't have to use different sound packs for different accounts.
* post Footer (optional): This allows you to automatically append some text to the end of your posts. Like a hashtag if posting about an event.

## Soundpacks

FastSM supports soundpacks, allowing you to customize FastSM to sound however you like! The official soundpacks repository can be found [here](https://github.com/FastSMApp/FastSM-soundpacks). To use a soundpack, put the folder containing all the sounds into either the sounds folder in your FastSM directory, or in .config/FastSM/sounds. Select it from the list in account options, and you're good to go!

Enjoy!
