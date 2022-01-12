# partial imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from time import sleep
from datetime import datetime, timedelta
# full imports
import sqlite3
import logging
import os
import random
import getpass

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
NORMAL_LOAD_AMMOUNT = 3
ONE_HOUR = 3600

def rand_dist():
	rand_number = random.randint(1,23)
	if rand_number in [1,2,3]:
		return random.randint(10,ONE_HOUR)
	elif rand_number in [4,5,6]:
		return random.randint(ONE_HOUR,2*ONE_HOUR)
	elif rand_number in [7,8,9,10]:
		return random.randint(2*ONE_HOUR,3*ONE_HOUR)
	elif rand_number in [11,12,13]:
		return random.randint(3*ONE_HOUR,4*ONE_HOUR)
	elif rand_number in [14,15,16]:
		return random.randint(4*ONE_HOUR,5*ONE_HOUR)
	elif rand_number in [17,18]:
		return random.randint(5*ONE_HOUR,6*ONE_HOUR)
	elif rand_number in [19,20]:
		return random.randint(6*ONE_HOUR,7*ONE_HOUR)
	elif rand_number in [21]:
		return random.randint(7*ONE_HOUR,8*ONE_HOUR)
	elif rand_number in [22]:
		return random.randint(8*ONE_HOUR,9*ONE_HOUR)
	elif rand_number in [23]:
		return random.randint(9*ONE_HOUR,10*ONE_HOUR)

def rand_fb_site():
	marketplace = 'https://www.facebook.com/marketplace/?ref=bookmark'
	notifications = "https://www.facebook.com/notifications"
	friends = 'https://www.facebook.com/friends'
	settings = 'https://www.facebook.com/settings/?tab=account'
	welcome_pg = 'https://www.facebook.com/?sk=welcome'
	sites = [marketplace,notifications,friends,settings,welcome_pg]
	return sites[random.randint(0,4)]

def load_more(n, sec):
	# Scroll down n times to load more elements
	for i in range(n):
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		sleep(sec)

def get_date():
	now = datetime.now()
	formatted_date = now.strftime(DATE_FORMAT)
	return formatted_date

def login():
	log.info("Logging in")
	driver.get("https://www.facebook.com")
	driver.find_element(By.XPATH,"//*[text() = 'Accept All']").click()
	sleep(1)
	email = input("Enter email: ")
	password = getpass.getpass("Enter password: ")
	driver.find_element(By.NAME,"email").send_keys(email)
	driver.find_element(By.NAME,"pass").send_keys(password)
	driver.find_element(By.XPATH,"//*[text() = 'Log In']").click()


def analize_weekly_liked_posts():
	driver.get("https://www.facebook.com/100065228954924/allactivity?category_key=ALL")
	while True:
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		days = driver.find_elements_by_xpath("//div[@class='kvgmc6g5 sj5x9vvc sjgh65i0 l82x9zwi uo3d90p7 pw54ja7n ue3kfks5 hybvsw6c']")
		if len(days) > 8:
			break
		sleep(5)

	days = days[:7]
	weekly_amount_of_likes = []
	for day in days:
		likes_per_day = day.find_elements_by_xpath(".//div[@class='l9j0dhe7 btwxx1t3 j83agx80']")
		likes = 0
		for like in likes_per_day:
			txt = like.find_element_by_xpath(".//div[@class='qzhwtbm6 knvmm38d']").text
			if 'likes' or 'reacted' in txt:
				likes += 1
		weekly_amount_of_likes.append(likes)
		likes = 0

	avg_amount_of_likes_per_day = int(sum(weekly_amount_of_likes)/len(weekly_amount_of_likes))

	return avg_amount_of_likes_per_day

def select_pages(categID):
	load_more(NORMAL_LOAD_AMMOUNT, 3)
	urls = driver.find_elements_by_tag_name('a')
	urls = [a.get_attribute('href') for a in urls]
	return_urls = []
	for url in urls:
		if url.endswith('?__tn__=%3C'):
			return_urls.append((url.split('?__tn__=%3C')[0],categID))
	return return_urls

def delete_element(element):
	driver.execute_script("""var element = arguments[0];
							element.parentNode.removeChild(element);
							""", element)


def like_rand(pagename, first_visit, avg_amount_of_likes_per_day, eff_privacy):
	amount_of_likes = 0
	pagename_short = pagename.split("https://www.facebook.com/")[1]
	try: pagename_short = pagename_short.split("/")[0]
	except:pass
	# Check Chatbox element and delete it
	try:
		chatbox = driver.find_element_by_xpath('//div[starts-with(@aria-label, "Chat with")]')
		delete_element(chatbox)
	except NoSuchElementException: 
		pass

	if first_visit:
		# Like page
		log.info("First visit on: "+pagename)
		os.mkdir("userdata/"+pagename_short)
		try:
			main_element = driver.find_element_by_xpath('//div[@style="top: 56px;"]//div[@aria-label="Like"]')
			main_element.click()
		except Exception as e:
			log.info(e)

	# Delete banner elements
	try:
		banner_0 = driver.find_element_by_xpath('//div[@style="top: 56px; z-index: 1;"]')
		delete_element(banner_0)
	except:
		banner_1 = driver.find_element_by_xpath('//div[@style="top: 56px;"]')
		delete_element(banner_1)
	banner_2 = driver.find_element_by_xpath('//div[@role="banner"]')
	delete_element(banner_2)

	# Connect to database
	conn = sqlite3.connect('userdata/likes.db')
	c = conn.cursor()

	# Randomly like posts
	last_element = ''
	while True:
		article_elements = driver.find_elements_by_xpath("//div[@class='lzcic4wl']")
		if last_element != '':
			indx = article_elements.index(last_element)
			article_elements = article_elements[indx+1:]

		# Go through every element
		for article_element in article_elements:
			last_element = article_element
			article_element.location_once_scrolled_into_view
			try:
				check_if_liked = article_element.find_element_by_xpath('.//div[@aria-label="Remove Like"]')
				sleep(random.randint(3,7))
				continue
			except NoSuchElementException:
				pass
			sleep(random.randint(3,20))
			try:
				decide_like = bool(random.randint(0,1))
				if decide_like:
					link_element = article_element.find_element_by_xpath('.//a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]')

					action = ActionChains(driver)
					try: action.move_to_element(link_element).perform()
					except: pass
					sleep(1)
					action.move_by_offset(500, 0).perform()
					sleep(2)

					post_url = article_element.find_element_by_xpath('.//a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]').get_attribute('href')
					post_url = post_url.split('__cft__')[0]
				
					# Save screenshot
					data = article_element.screenshot_as_png
					with open("userdata/"+pagename_short+"/"+get_date()+".png",'wb') as f:
						f.write(data)

					# Like post
					like_element = article_element.find_element_by_xpath('.//div[@aria-label="Like"]')
					like_element.location_once_scrolled_into_view
					like_element.click()
					amount_of_likes += 1

					# Save post to database
					c.execute('INSERT INTO "' + pagename + '" (post, time) \
							VALUES ("' + post_url + '","' + get_date() + '")');
					conn.commit()
					log.info("Liked {} post on page {}".format(post_url, pagename))
					sleep(random.randint(1,5))
					del action
			except Exception as e:
				log.info(e)

		random_addition = int(avg_amount_of_likes_per_day*0.2)
		random_break = random.randint(-random_addition,random_addition)
		# avg pages per day == 7
		if amount_of_likes > ((avg_amount_of_likes_per_day + random_break) * (eff_privacy/0.5)) / 7:
			log.info("Random loop break")
			break
		sleep(random.randint(3,10))

	conn.close()
		

def new_page(pagename):
	conn = sqlite3.connect('userdata/likes.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE "{}"
	             ([post] text PRIMARY KEY,
	              [time] date)'''.format(pagename))
	conn.commit()
	conn.close()

def new_keyword(keyword):
	conn = sqlite3.connect('userdata/pages.db')
	c = conn.cursor()
	c.execute('INSERT INTO categories (category) \
			  		   VALUES (?)', [keyword])
	conn.commit()
	ID = c.lastrowid
	conn.close()
	return ID

def create_categ_table():
	conn = sqlite3.connect('userdata/pages.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE categories
	             ([ID] INTEGER PRIMARY KEY,
	              [category] text)''')
	c.execute('''CREATE TABLE pages
	             ([PID] INTEGER PRIMARY KEY,
	              [URL] text,
	              [categID] int)''')
	conn.commit()
	conn.close()

def main():
	global driver
	global log

	log = logging.getLogger()
	log.setLevel(logging.INFO)
	fileformat = logging.Formatter("%(asctime)s: %(message)s",
									datefmt=DATE_FORMAT)

	file = logging.FileHandler("bot_logs.log")
	file.setFormatter(fileformat)
	log.addHandler(file)

	console = logging.StreamHandler()
	console.setFormatter(fileformat)
	log.addHandler(console)

	profile_path = '/home/'+ os.getlogin() + '/.mozilla/firefox/' 
	try:
		profile_path += [a for a in os.listdir(profile_path) if a.endswith('.default-esr')][0]
	except IndexError:
		profile_path += [a for a in os.listdir(profile_path) if a.endswith('.default-release')][0]
	fx_prof = webdriver.FirefoxProfile(profile_path)

	#exec_path = input("Enter geckodriver executable path:")
	exec_path = '/home/'+ os.getlogin() + '/Downloads/geckodriver/geckodriver'

	keyword = input("Enter search keyword: ")
	keyword = keyword.replace(" ","+")
	eff_privacy = int(input("Enter desired privacy (1-100): "))
	eff_privacy = eff_privacy / 100
	
	try: 
		os.mkdir("userdata")
	except FileExistsError:
		pass
	driver = webdriver.Firefox(executable_path = exec_path,firefox_profile = fx_prof)

	if os.path.isfile('userdata/avg_daily_posts'):
		with open('userdata/avg_daily_posts','r') as f:
			avg_amount_of_likes_per_day = int(f.read())
	else:
		avg_amount_of_likes_per_day = analize_weekly_liked_posts()
		with open('userdata/avg_daily_posts','w') as f:
			f.write(str(avg_amount_of_likes_per_day))
	

	# get tables from database
	conn = sqlite3.connect('userdata/pages.db')
	c = conn.cursor()

	try:
		c.execute("SELECT category FROM categories")
	except sqlite3.OperationalError:
		create_categ_table()
	keywords_in_db = c.fetchall()
	conn.close()

	rand_ste = rand_fb_site()
	driver.get(rand_ste)
	sleep(5)

	if (keyword,) not in keywords_in_db:
		categID = new_keyword(keyword)
		search_url = 'https://www.facebook.com/search/pages?q=' + keyword
		log.info("GET: "+ search_url)
		driver.get(search_url)
		sleep(5)

		page_urls = select_pages(categID)
		info = "Pages selected for keyword '{}':".format(keyword)
		log.info(info)
		for page_url in page_urls:
			log.info("   "+ page_url[0])

		conn = sqlite3.connect('userdata/pages.db')
		c = conn.cursor()
		c.executemany('INSERT INTO pages (URL, categID) \
			  		   VALUES (?, ?)', page_urls);
		conn.commit()
		conn.close()

	# get tables from database
	conn = sqlite3.connect('userdata/pages.db')
	c = conn.cursor()
	c.execute("SELECT * FROM pages")
	urls = c.fetchall()
	conn.close()
	'''
	urls_1 = []
	urls_2 = []

	for url in urls:
		if url[2] == 1:
			urls_1.append(url)
		else:
			urls_2.append(url)

	random.shuffle(urls_1)
	random.shuffle(urls_2)
	'''

	# get tables from database
	conn = sqlite3.connect('userdata/likes.db')
	c = conn.cursor()
	c.execute("SELECT name FROM sqlite_master WHERE type='table';")
	urls_in_db = c.fetchall()
	conn.close()

	#counter = 1
	#for i in range(len(urls)):
	for url in urls:
		#randn = random.randint(1,10)
		'''
		if (counter % 5) == 1:
			url = urls_2[0][1]
			urls_2.pop(0)
		else:
			url = urls_1[0][1]
			urls_1.pop(0)
		'''
		url = url[1]
		log.info("GET: "+ url)
		driver.get(url)
		sleep(10)

		if ((url,)) in urls_in_db:
			like_rand(url, False, avg_amount_of_likes_per_day, eff_privacy)
		else:
			new_page(url)
			like_rand(url, True, avg_amount_of_likes_per_day, eff_privacy)

		rand_site = rand_fb_site()
		driver.get(rand_site)
		# wait between 10s and 10 hours
		randtime = rand_dist()
		time_formatted = str(timedelta(seconds = randtime))
		log.info("Wait for "+ time_formatted + " (hh:mm:ss)")
		sleep(randtime)
		#counter += 1

main()
