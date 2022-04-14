# MetaPriv
An automated tool that allows Facebook users to obfuscate their data and conceal their real interests and habits from Facebook

#### How it works (high level):
1. Opens a browser instance – Firefox or Chrome/Chromium.
2. Opens facebook.com and logs in.
3. Opens facebook.com/search/pages?q=keyword, collects data related to that keyword and stores the corresponding URLs in a database.
4. Selects a random URL from the database and opens it in the browser.
5. Clicks the page’s ”like” button then moves to the first post element.
6. Waits between 3 and 10 seconds. Decides whether to like the post, then moves to the next element.
7. Repeats step 6 in a loop. When moving to the next element, the page will scroll down, loading more post elements.
8. Breaks the loop based on an inputted privacy value, then goes back to step 4 and repeats the remaining steps.

#### Requirements:
- python3
- python3 libraries: pip install -r requirements.txt
- tkinter: sudo apt install python3-tk / sudo pacman -S tk

## How to use:
#### On Linux (tested on Manjaro):
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


#### On Windows:
1. Install the requirements.
2. Run command: python main.py
3. On first run with Firefox: 
	- Create a password. It will be used to encrypt your credentials, database and logs.
	- Input facebook credentials, a seed keyword and your preferred browser (Firefox/Chrome).
	- Choose desired privacy level and click start.
	- To close the program -- close the window.
4. On next runs with Firefox:
	- Input the password you created on the first run.
	- Choose desired privacy level and click start.
5. With Chrome it will always log in.

No exe for Windows since pyinstaller doesn't seem to work properly...

## Code description:
Consists of 4 files:
#### 1. crypto.py
- encryption and decryption ([AES-256](https://pycryptodome.readthedocs.io/en/latest/src/cipher/aes.html)) 
- hashing ([SHA256](https://docs.python.org/3/library/hashlib.html)) 
#### 2. passwordclass.py
- Create_Password_UI:
	- Opens a window where the user can enter and reenter a password (standard password creation). There is also an option to hide/show the password. The only requirement is minimum 8 characters.
	- The password is verified with it's reentry. If:
		- It matches - the window closes and the program continues it's normal course.
		- It doesn't match - a 'Retry' comment is displayed. The program will not continue untill the passwords match.
	- If the user closes the window. The window closes and the program stops execution with sys.exit()
	- The password is then used by the firstlaunchclass.py file.
- Enter_Password_UI:
	- Opens a window where the user has to enter the password created on the first run. There is also an option to hide/show the password.
	- After input, it opens the file .saved_data and gets the hash(random_number + password) and random_number from there.
	- Then it hashes hash(random_number + input_password) and compares the two. If:
		- It matches - the window closes and the program continues it's normal course.
		- It doesn't match - a 'Retry' comment is displayed. The program will not continue untill the password is correct.
	- If the user closes the window. The window closes and the program stops execution with sys.exit()

#### 3. firstlaunchclass.py
- Password creation: 
	- It calls Create_Password_UI from passwordclass.py and gets the password from it. The password is then hashed. It will be used by main.py for AES encryption and decryption.
	- Creates a random 32 byte number with os.urandom(32).
	- A hash(random_number + password) variable is created and stored in a file .saved_data
	- After, it deletes the variable assigned to the Create_Password_UI class so that the plaintext password is not stored in memory.
- Facebook credential input:
	- Email: someone@somemail.something
	- Password. There is also an option to hide/show the password.
	- The credentials are encrypted with the hashed password and stored in .saved_data
- Keyword input:
	- A seed keyword input. The next keywords will be generated automatically.
	- The encrypted keyword is stored in .saved_data along with the number of times it was used (so 0 in this case). Enc(keyword + '|0')
	- A timestamp variable is created.
	- An HMAC of the keyword is created with hash(hashed_password + timestamp + keyword).
- Browser choice:
	- Firefox or Chrome.
	- Stored in an encrypted form in .saved_data

#### 4. main.py
- main function:
	- Checks if .saved_data file exists. If:
		- Yes. Calls Enter_Password_UI from passwordclass.py, gets the hashed password and assigs it to the key variable used for AES encryption and decryption. Then, it deletes the variable assigned to the Enter_Password_UI class.
		- No. Calls First_launch_UI from firstlaunchclass.py gets the hashed password and assigs it to the key variable used for AES encryption and decryption. Then, it deletes the variable assigned to the First_launch_UI class.
	- Calls the Userinterface class that opens the main window. Passes the key variable as an argument
- Userinterface:
	- Creates a main window with:
		- A canvas for displaying screenshots later.
		- An INFO text.
		- A slider to choose the privacy level (default 55).
		- A scrolled text widget for displaying logs. The logs are taken from bot_logs.log
		- A start button. When clicking start:
			- Calls the BOT calss by running BOT.start_bot as a different process with pythons [multiprocessing](https://docs.python.org/3/library/multiprocessing.html) library. Passes the key variable and eff_privacy variable from the slider as arguments.
			- Disables the slider and button and creates a screenshot label on top of them.
			- Starts updating the UI recursevly every 2 seconds. The update consists of displaying .screenshot.png and getting the last log from bot_logs.log
- BOT:
	- start_bot:
		- Gets the browser choice (Firefox/Chrome) from .saved_data
		- Creates bot_logs.log if it doesn't exist.
		- Starts the selenium webdriver in headless mode based on browser choice.
		- On first run it uses a default browser profile (stored in the OS temp folder), logs in then copies the browser profile from temp to the folder that MetaPriv is ran from. On the next runs, the BOT will use it so that it doesn't need to log in again.
		- Creates a thread for taking browser screenshots every second. These are saved in .screenshot.png 
		- Creates a user_data folder if it doesn't exist.
		- Gets the average amount of likes per day from the Facebook profile. 
			- On first run, calls analize_weekly_liked_posts() which goes to the [profiles logged activity page](https://www.facebook.com/100065228954924/allactivity?category_key=ALL) and calculates the average ammount of likes or activities per day from the last week. This is done by counting the activity elements from the first 7 day elements. The page is scrolled down untill 7 day elements are displayed. The variable is then stored in an encrypted form in userdata/supplemtary.
			- On next runs, it gets the variable by decrypting the value stored in userdata/supplemtary.
		- Calls generate_noise function. The arguments are browser choice, average amount of likes per day variable, eff_privacy and key.
	- generate_noise:
		- Calls pages_based_on_keyword function:
			- Verifies the keyword intergity by calling check_keyword which decripts the keyword_line and gets the timestamp from .saved_data, then creates the hmac and compares it with the saved hmac from .saved_data. The function returns the keyword and usage number (how many times the keyword was used).
			- Encrypts the keyword, opens or creates and opens userdata/pages.db and gets the keywords stored in it. If:
				- The keyword is already in the db: checks if the number of usages exceeds the number of pages in the db related to the keyword. If it does, it generates a new keyword by calling gen_keyword which:
					- opens a tempral selenium webdriver in headless mode
					- goes to relatedwords.org/relatedto/keyword
					- gets the top 5 suggestions and chooses a random one from these then returns the new keyword.
					- closes the driver
				- The keyword is not in the db: adds the keyword to the db and goes to facebook.com/search/pages?q=keyword. Then, it calls select_pages which takes the first FB page urls from the webpage and returns 8-15 of them. These pages are then stored encrypted in the db.
		- Gets the FB pages based on the keyword from userdata/pages.db
		- Gets urls from already liked pages from userdata/likes.db or creates the database.
		- Goes though every url in a loop that:
			- goes to url and calls like_rand if the url is in userdata/likes.db or adds the url to userdata/likes.db and calls like_rand if not.
			- updates the keyword usage by calling the function update_keyword updates the usage_number of the keyword and genrates a new hmac.
			- waits a random amount of time between 10 seconds and 10 hours before going to the next url.
	- like_rand:
		- Tries to delete the Chatox and banner elements from the page. If it fails, then pass.
		- Tries to like the page. If it fails, then pass.
		- Creates a random value between -40% and +40% to the avg_amount_of_likes_per_day variable and assigns it to a variable random_break. This will be used to break an infinite scrolling loop.
		- In an infinite loop, go through every element in the page and decide to like it or not randomly: bool(random.randint(0,1)). By going to the next element, more elements are loaded so it never ends unless the FB page runs out of posts.
		- If the decision is to like, then the post link is saved in userdata/likes.db
		- The loop breaks if the amount of likes becomes more than ((avg_amount_of_likes_per_day + random_break) * (eff_privacy/0.5)) / 7. It is divided by 7 since on average the BOT goes through 7 pages per day (if running constantly 24/7). The value can be changed by the user in the code and a screenshot of every post can be made by uncommenting the Save screenshot part from the loop.
	- other functions in the calss BOT:
		- load_more - scroll down the page n times based on the parameter n that is passed to the function
		- login - goes to facebook.com, clicks Allow All Cookies button, puts the credentials in their respective boxes, then clicks Log In.
		- delete_element - deletes a specified page element.
		- quit_bot - closes the webdriver and joins the screenshot taking thread.
- other functions:
	- sleep - essentially time.sleep but the function stops if BREAK_SLEEP.value becomes True which happens if the BOT is signalled to close.
	- new_page - add a url as a table to userdata/likes.db
	- new_keyword - add a new keyword in userdata/pages.db
	- create_categ_table - creates userdata/pages.db
	- rand_dist - returns a random value between 10 seconds and 10 hours. High probability of 10s to 5h. Low probability of 5h to 10h.
	- rand_fb_site - returns a random FB url. This is where the webdriver goes to when it waits.
	- write_log - writes encrypted logs to bot_logs.log
	- get_date - gets the date and time in a nice format.

#### Files created by MetaPriv:
- .saved data:
	- First line: Encrypted FB email
	- Second line: Encrypted FB password
	- Third line: Encrypted keyword+|+usage_number
	- Fourth line: Encrypted browser choice
	- Fifth line: Random number
	- Sixth line: Hash(random number + user password)
	- Seventh line: HMAC(user password + timestamp + encrypted keyword)

- bot_logs.log: encrypted logs
- driver.log: logs made by the webdriver
- userdata/supplementary: stores the encrypted average amount of likes per day
- userdata/pages.db:
	- table 1 - categories:
		- ID column (stores ID of the keyword)
		- category column (stores encrypted keywords)
	- table 2 - pages:
		- PID (ID of the URL)
		- URL (stores the encrypted urls)
		- categID (ID corresponding to the keyword from the categories table)
- userdata/likes.db:
	- Every table is an encrypted FB page URL
	- Each table has a post column (stores the encrypted url of a liked post from that page) and a time column (stores the timestamp)

Optional:

By uncommenting the Save screenshot part from the loop in BOT.like_rand, the program can take screenshots of every post and save them in a folder corresponding to the name of the FB page (e.g. userdata/somepage/%Y-%m-%d %H:%M:%S.png)
