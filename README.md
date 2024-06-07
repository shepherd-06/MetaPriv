# MetaPriv
An automated tool that allows Facebook users to obfuscate their data and conceal their real interests and habits from Facebook.

#### How it works (high level):
1. Opens a browser instance – Firefox.
2. Opens facebook.com and logs in.
3. Opens facebook.com/search/pages?q=keyword, collects data related to that keyword and stores the corresponding URLs in a database.
4. Selects a random URL from the database and opens it in the browser.
5. Clicks the page’s ”like” button then moves to the first post element.
6. Waits between 3 and 10 seconds. Decides whether to like the post, then moves to the next element.
7. Repeats step 6 in a loop. When moving to the next element, the page will scroll down, loading more post elements.
8. Breaks the loop based on a privacy value.
9. Goes to Facebook's main feed and clicks ads from there.
10. Searches for videos related to the keyword and watches them.
11. Goes to step 4 and repeats the remaining steps.

You can have the app constantly running in the background on your machine. It will stop when your machine goes to sleep. Then, it will automaticaly resume when your machine wakes up from sleep.

#### Requirements:
- python3
- python3 libraries: pip install -r requirements.txt
- tkinter: sudo apt install python3-tk / sudo pacman -S tk
- firefox

## How to use:
#### On Linux:
1. Install the requirements.
2. Run command: python main.py
3. On first run: 
	- Create a password. It will be used to encrypt your credentials, database and logs.
	- Input facebook credentials and a seed keyword.
	- Choose desired privacy (noise likes per day) value and click start.
	- To close the program -- close the window.
4. On next runs:
	- Input the password you created on the first run.
	- Choose desired privacy level and click start.

# Paper
https://arxiv.org/abs/2209.03679
https://link.springer.com/chapter/10.1007/978-3-031-25538-0_36
