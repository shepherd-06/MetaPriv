# MetaPriv
An automated tool that allows Facebook users to obfuscate their data and conceal
their real interests and habits from Facebook

How it works:

1. Opens a browser instance – Firefox or Chrome/Chromium.
2. Opens https://www.facebook.com and logs in.
3. Opens https://www.facebook.com/search/pages?q=keyword, collects data related to that keyword and stores the corresponding URLs in a database.
4. Selects a random URL from the database and opens it in the browser.
5. Clicks the page’s ”like” button then moves to the first post element.
6. Waits between 3 and 10 seconds. Decides whether to like the post, then moves to the next element.
7. Repeats step 6 in a loop. When moving to the next element, the page will scroll down, loading more post elements.
8. Breaks the loop based on an inputted privacy value, then goes back to step 4 and repeats the remaining steps.

Requirements:
- python3
- python3 libraries: pip install -r requirements.txt
- tkinter: sudo apt install python3-tk / sudo pacman -S tk

# How to use:
On Linux (tested on Manjaro):
1. Install the requirements.
2. Run command: python main.py
3. On first run: 
	- Create a password. It will be used to encrypt your credentials, database and logs.
	- Input facebook credentials, a seed keyword and your preferred browser (Firefox/Chrome).
	- Choose desired privacy level and click start.
	- To close the program -- close the window.
4. On next runs:
	- Input the password you created on the first run.
	- Choose desired privacy level and click start.

OR:
Download executable from: https://github.com/ctrgrb/MetaPriv/releases/tag/v0.1 and run.

On Windows:
1. Working on it...
