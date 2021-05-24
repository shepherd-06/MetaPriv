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

def select_pages():
	load_more(NORMAL_LOAD_AMMOUNT, 3)
	urls = driver.find_elements_by_tag_name('a')
	urls = [a.get_attribute('href') for a in urls]
	return_urls = []
	for url in urls:
		if url.endswith('?__tn__=%3C'):
			return_urls.append(url.split('?__tn__=%3C')[0])
	return return_urls

def delete_element(element):
	driver.execute_script("""var element = arguments[0];
							element.parentNode.removeChild(element);
							""", element)


def like_all(pagename, first_visit):
	pagename_short = pagename.split('/')[-2]
	# Check first element
	first_element = driver.find_element_by_xpath("//div[@role='article']")
	try:
		check_first = first_element.find_element_by_xpath('.//div[@aria-label="Remove Like"]')
		log.info("No new posts on page {}".format(pagename))
		return
	except NoSuchElementException:
		pass

	# Check Chatbox element and delete it
	try:
		chatbox = driver.find_element_by_xpath('//div[starts-with(@aria-label, "Chat with")]')
		delete_element(chatbox)
	except NoSuchElementException: 
		pass

	ammount = 0
	if first_visit:
		# Like page
		log.info("First visit on: "+pagename)
		os.mkdir("userdata/"+pagename_short)
		try:
			main_element = driver.find_element_by_xpath('//div[@style="top: 56px;"]//div[@aria-label="Like"]')
			main_element.click()
			ammount = 10
		except Exception as e:
			log.info(e)
	else:
		ammount = 3

	# Delete banner elements
	banner_1 = driver.find_element_by_xpath('//div[@style="top: 56px;"]')
	delete_element(banner_1)
	banner_2 = driver.find_element_by_xpath('//div[@role="banner"]')
	delete_element(banner_2)
	
	# Scroll down to load more elements
	load_more(ammount,7)

	# Connect to database
	conn = sqlite3.connect('userdata/likes.db')
	c = conn.cursor()
	c.execute('SELECT * FROM "' + pagename + '"')
	posts_date = c.fetchall()
	posts = []
	for post in posts_date:
		posts.append(post[0])

	# Like posts
	article_elements = driver.find_elements_by_xpath("//div[@class='lzcic4wl']")
	
	# Scroll to top
	driver.execute_script("window.scrollTo(0,0);")
	sleep(1)

	# Go through every element
	for article_element in article_elements:
		try:
			link_element = article_element.find_element_by_xpath('.//a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]')
			link_element.location_once_scrolled_into_view

			action = ActionChains(driver)
			try: action.move_to_element(link_element).perform()
			except: pass
			sleep(1)
			action.move_by_offset(-200, 0).perform()
			#except: pass
			sleep(2)

			post_url = article_element.find_element_by_xpath('.//a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]').get_attribute('href')
			post_url = post_url.split('__cft__')[0]

			# move on if post in database
			if post_url in posts:
				continue
			
			# Save screenshot
			article_element.location_once_scrolled_into_view
			data = article_element.screenshot_as_png
			with open("userdata/"+pagename_short+"/"+get_date()+".png",'wb') as f:
				f.write(data)

			# Like post
			like_element = article_element.find_element_by_xpath('.//div[@aria-label="Like"]')
			like_element.location_once_scrolled_into_view
			like_element.click()

			# Save post to database
			c.execute('INSERT INTO "' + pagename + '" (post, time) \
					VALUES ("' + post_url + '","' + get_date() + '")');
			conn.commit()
			log.info("Liked {} post on page {}".format(post_url, pagename))
			del action
		except Exception as e:
			log.info(e)

	conn.close()


def like_rand(pagename, first_visit):
	pagename_short = pagename.split('/')[-2]
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
					#link_element.location_once_scrolled_into_view

					action = ActionChains(driver)
					try: action.move_to_element(link_element).perform()
					except: pass
					sleep(1)
					action.move_by_offset(500, 0).perform()
					sleep(2)

					post_url = article_element.find_element_by_xpath('.//a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]').get_attribute('href')
					post_url = post_url.split('__cft__')[0]
				
					# Save screenshot
					#article_element.location_once_scrolled_into_view
					data = article_element.screenshot_as_png
					with open("userdata/"+pagename_short+"/"+get_date()+".png",'wb') as f:
						f.write(data)

					# Like post
					like_element = article_element.find_element_by_xpath('.//div[@aria-label="Like"]')
					like_element.location_once_scrolled_into_view
					like_element.click()

					# Save post to database
					c.execute('INSERT INTO "' + pagename + '" (post, time) \
							VALUES ("' + post_url + '","' + get_date() + '")');
					conn.commit()
					log.info("Liked {} post on page {}".format(post_url, pagename))
					sleep(random.randint(1,5))
					#rand_scroll = random.randint(230,300)
					#scroll = "window.scrollBy(0,{})".format(rand_scroll)
					#driver.execute_script(scroll)
					del action
			except Exception as e:
				log.info(e)

		# 1/6 chance of breaking the infinite while loop
		random_break = random.randint(1,6)
		if random_break == 1:
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
	c.execute('''CREATE TABLE "{}"
	             ([page] text PRIMARY KEY,
	              [time] date)'''.format(keyword))
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

	keyword = input("Enter search keyword: ")
	keyword = keyword.replace(" ","+")

	# get tables from database
	conn = sqlite3.connect('userdata/pages.db')
	c = conn.cursor()
	c.execute("SELECT name FROM sqlite_master WHERE type='table';")
	keywords_in_db = c.fetchall()
	conn.close()

	profile_path = '/home/'+ os.getlogin() + '/.mozilla/firefox/' 
	profile_path += [a for a in os.listdir(profile_path) if a.endswith('.default-release')][0]
	fx_prof = webdriver.FirefoxProfile(profile_path)

	#exec_path = input("Enter geckodriver executable path:")
	exec_path = '/home/'+ os.getlogin() + '/Downloads/geckodriver/geckodriver'
	driver = webdriver.Firefox(executable_path = exec_path,firefox_profile = fx_prof)
	
	rand_ste = rand_fb_site()
	driver.get(rand_ste)
	sleep(5)

	if (keyword,) not in keywords_in_db:
		new_keyword(keyword)
		search_url = 'https://www.facebook.com/search/pages?q=' + keyword
		log.info("GET: "+ search_url)
		driver.get(search_url)
		sleep(5)

		page_urls = select_pages()
		info = "Pages selected for keyword '{}':".format(keyword)
		log.info(info)
		for page_url in page_urls:
			log.info("   "+ page_url)
		
		List_of_Tuples = []
		for page_url in page_urls:
			List_of_Tuples.append((page_url,get_date()))

		conn = sqlite3.connect('userdata/pages.db')
		c = conn.cursor()
		c.executemany('INSERT INTO "' + keyword + '" (page, time) \
			  		   VALUES (?, ?)', List_of_Tuples);
		conn.commit()
		conn.close()

	# get tables from database
	conn = sqlite3.connect('userdata/pages.db')
	c = conn.cursor()
	c.execute("SELECT name FROM sqlite_master WHERE type='table';")
	keywords_in_db = c.fetchall()

	# database to datastructure
	urls = []
	for keyword in keywords_in_db:
		c.execute('SELECT * FROM "' + keyword[0] + '"')
		List_of_Tuples = c.fetchall()
		for tpl in List_of_Tuples:
			urls.append(tpl[0])
	conn.close()
	random.shuffle(urls)

	# get tables from database
	conn = sqlite3.connect('userdata/likes.db')
	c = conn.cursor()
	c.execute("SELECT name FROM sqlite_master WHERE type='table';")
	urls_in_db = c.fetchall()
	conn.close()

	for url in urls:
		log.info("GET: "+ url)
		driver.get(url)
		sleep(10)
		if ((url,)) in urls_in_db:
			like_rand(url, False)
		else:
			new_page(url)
			like_rand(url, True)

		rand_site = rand_fb_site()
		driver.get(rand_site)
		# wait between 10s and 10 hours
		randtime = rand_dist()
		time_formatted = str(timedelta(seconds = randtime))
		log.info("Wait for "+ time_formatted + " (hh:mm:ss)")
		sleep(randtime)

main()