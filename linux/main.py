# selenium imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
## for firefox
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
# partial imports
from time import sleep as Sleep
from datetime import timedelta, datetime
from tempfile import gettempdir
from shutil import copytree
from base64 import b64encode
# full imports
import tkinter as tk
import tkinter.scrolledtext as ScrolledText
import multiprocessing as mp
import os
import random
import getpass
import threading
import sqlite3
import sys
# imports from created files 
from firstlaunchclass import First_launch_UI
from passwordclass import Enter_Password_UI
from stats import StatsWindow
from crypto import Hash, aes_encrypt, aes_decrypt


NORMAL_LOAD_AMMOUNT = 2
ONE_HOUR = 3600
QUIT_DRIVER = mp.Value('b', False)
BREAK_SLEEP = mp.Value('b', False)
STOP_WATCHING = mp.Value('b', False)
NEW_SEED = mp.Value('b', False)
CHECK_NET = mp.Value('b', True)
W = 'white'
INFO_TEXT = """[*] INFO [*]
In this window you should choose how many posts
to like per day on average. You can be change the
value on your next run.

To start adding noise to your account, press the Start Bot
Process button. To exit MetaPriv, close the window by 
pressing X on your window border. Sometimes it may take 
few seconds to close. 

For more information please refer to the documentation in the
github repository.
"""

#########################################################################################################################

class BOT:

	def update_keyword(self, key, new_word = None):
		# Increment keyword usage in file
		filepath = os.getcwd()+'/'+'.saved_data'
		with open(filepath, "r") as f1:
		   text = f1.read()
		text = text.split('\n')
		if new_word == None:
			keyword_line = aes_decrypt(text[2],key)
			word, usage_number = keyword_line.split('|')
			usage_number = int(usage_number) + 1
		else:
			word = new_word
			usage_number = 0
		text[2] = aes_encrypt(word + '|' + str(usage_number),key)
		timestamp = get_date()
		new_hmac = b64encode(Hash(b64encode(key).decode('utf-8') + timestamp + text[2])).decode('utf-8')
		text[6] = new_hmac
		text[7] = timestamp
		text = '\n'.join(text)
		with open(filepath, "w") as f2:
			f2.write(text)

	def check_keyword(self,key):
		with open(os.getcwd()+'/'+'.saved_data','r') as f:
			text = f.read()
			text = text.split('\n')
			keyword_line = text[2]
			dec_keyword = aes_decrypt(keyword_line,key).split('|')
			keyword = dec_keyword[0]
			usage_number = int(dec_keyword[1])
			timestamp = text[7]
			HMAC = text[6]
		# Verify keyword integrity
		hmac = b64encode(Hash(b64encode(key).decode('utf-8') + timestamp + keyword_line)).decode('utf-8')
		if hmac != HMAC:
			write_log("[!] Protocol broken!!!",key)
			self.quit_bot()
			sys.exit()
		return keyword, usage_number

	def gen_keyword(self, keyword, key):
		# Generate new keywords from https://relatedwords.org
		write_log(get_date()+": "+"Generating new keyword...",key)
		# Open temporary driver
		fx_options = Options()
		fx_options.add_argument("--headless")
		driverpath = os.environ['HOME'] + "/.wdm/drivers/geckodriver/linux64/"
		versions = os.listdir(driverpath)
		versions.sort()
		version = versions[-1]
		driverpath = driverpath + version + "/geckodriver"
		temp_driver = webdriver.Firefox(service=Service(driverpath),options = fx_options)
		url = 'https://relatedwords.org/relatedto/' + keyword.lower()
		temp_driver.get(url)
		word_elements = temp_driver.find_elements(By.XPATH, "//a[@class='item']")[:5]
		# Get words
		words = []
		for word_element in word_elements:
			words.append(word_element.text)
		# Close driver
		temp_driver.quit()
		# Choose a random word from top 5 
		pseudo_random_word = words[random.randint(0,4)]
		write_log(get_date()+": "+"Done! New keyword: "+pseudo_random_word,key)
		sleep(2)
		self.update_keyword(key, pseudo_random_word)
		return pseudo_random_word

	def start_bot(self, eff_privacy, key):
		# Create log file
		if not os.path.isfile(os.getcwd()+'/bot_logs.log'):
			text = get_date()+": "+"First launch\n"
			print(text)
			with open(os.getcwd()+'/'+"bot_logs.log", "w") as f:
				f.write(aes_encrypt(text,key))

		tempdirs = []
		# Start webdriver
		# Check if browser profile folder exists
		profile_exists = os.path.isdir(os.getcwd()+'/fx_profile')
		if not profile_exists:
			tempdirs = os.listdir(gettempdir())
		# webdriver options
		fx_options = Options()
		profile_path = os.getcwd()+'/fx_profile'
		if profile_exists:
			fx_options.add_argument("--profile")
			fx_options.add_argument(profile_path)
		fx_options.add_argument("--headless")
		# Start
		self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options = fx_options)
		self.driver.set_window_size(1400,800)

		#eff_privacy = eff_privacy / 100
		
		sleep(3)
		
		# Start taking screenshots of the headless browser every second on different thread
		t1 = threading.Thread(target=self.take_screenshot, args=[])
		t1.start()

		if QUIT_DRIVER.value: self.quit_bot(t1)
		# Create userdata folder if it does not exist
		try: 
			os.mkdir(os.getcwd()+"/userdata")
		except FileExistsError:
			pass

		# Open random Facebook site
		rand_ste = rand_fb_site()
		self.driver.get(rand_ste)

		sleep(5)
		if QUIT_DRIVER.value: self.quit_bot(t1)
		
		# Create browser profile folder
		if not profile_exists:
			self.login(key)
			tempdirs_2 = os.listdir(gettempdir())
			for i in tempdirs_2:
				if i not in tempdirs:
					if 'mozprofile' in i:
						write_log(get_date()+": "+"Copying profile folder...",key)
						src = gettempdir() + '/' + i
						os.remove(src+'/lock')
						copytree(src, profile_path)


		t2 = threading.Thread(target=self.delete_chat, args=[])
		t2.start()
		self.generate_noise(eff_privacy, key)
		self.quit_bot(t1, t2)

	def delete_chat(self):
		while not QUIT_DRIVER.value:
			# Check Chatbox element and delete it
			try:
				chatbox = self.driver.find_element(By.XPATH, '//div[@data-testid="mwchat-tabs"]')
				self.delete_element(chatbox)
				print(get_date()+": "+"Deleted chatbox.")
			except: pass
			sleep(1)


	def generate_noise(self, eff_privacy, key):
		while True:

			if QUIT_DRIVER.value: return
			enc_keyword = self.pages_based_on_keyword(key)
			if QUIT_DRIVER.value: return

			# get urls from database based on current keyword
			conn = sqlite3.connect('userdata/pages.db')
			c = conn.cursor()
			c.execute('SELECT ID FROM categories WHERE category IS "'+enc_keyword+'"')
			ID = c.fetchall()
			c.execute('SELECT URL FROM pages WHERE categID IS '+str(ID[0][0]))
			urls = c.fetchall()
			conn.close()
			random.shuffle(urls)

			# get urls from liked pages from database
			conn = sqlite3.connect('userdata/likes.db')
			c = conn.cursor()
			c.execute("SELECT name FROM sqlite_master WHERE type='table';")
			liked_pages_urls = c.fetchall()
			conn.close()

			for (url,) in urls:
				if NEW_SEED.value:
					NEW_SEED.value = False
					break
				if (url,) in liked_pages_urls:
					continue
				dec_url = aes_decrypt(url, key)
				write_log(get_date()+": "+"GET: "+ dec_url,key)
				self.driver.get(dec_url)
				sleep(10)
				if QUIT_DRIVER.value: break
				# Start liking
				new_page(url)

				print_done = False
				while True:
					if QUIT_DRIVER.value: break
					date_now = get_date().split(' ')[0]
					if not os.path.isfile(os.getcwd()+'/'+'userdata/supplemtary'):
						with open(os.getcwd()+'/'+'userdata/supplemtary','w') as f:
							f.write(date_now + " 0")
					with open(os.getcwd()+'/'+'userdata/supplemtary','r') as f:
						saved_date, usage_this_day = f.read().split(' ')
					
					if date_now == saved_date:
						if int(usage_this_day) >= eff_privacy / 10:
							if not print_done:
								write_log(get_date()+": "+"Done for today.",key)
								print_done = True
								CHECK_NET.value = False
							sleep(60)
							continue
						else: break
					else:
						with open(os.getcwd()+'/'+'userdata/supplemtary','w') as f:
								f.write(date_now + " 0")
						CHECK_NET.value = True
						break

				if QUIT_DRIVER.value: break
				self.like_rand(dec_url, eff_privacy, key)
				# Increment keyword usage
				self.update_keyword(key)
				with open(os.getcwd()+'/'+'userdata/supplemtary','r') as f:
					saved_date, usage_this_day = f.read().split(' ')
				usage_this_day = int(usage_this_day)
				with open(os.getcwd()+'/'+'userdata/supplemtary','w') as f:
					f.write(get_date().split(' ')[0] + " " + str(usage_this_day+1))

				randtime = rand_dist(eff_privacy)
				if not QUIT_DRIVER.value:
					time_formatted = str(timedelta(seconds = randtime))
					#resume_time = datetime.now() + timedelta(0,randtime)
					#resume_time = resume_time.strftime('%Y-%m-%d %H:%M:%S')
					write_log(get_date()+": "+"Watching videos and clicking ads for "+ time_formatted + " (hh:mm:ss).",key)#" Resume liking at " + resume_time, key)
				sleep(5)
				if QUIT_DRIVER.value: break
				self.watch_videos(randtime, key)
				if QUIT_DRIVER.value: break


	def wait(self, randtime):
		time = 0
		while True:
			Sleep(1-0.003)
			time += 1
			if BREAK_SLEEP.value:
				break
			if time == randtime:
				break
		STOP_WATCHING.value = True

	def click_links(self, key):
		try:create_clicked_links_db()
		except sqlite3.OperationalError: pass
		self.driver.get('https://www.facebook.com/')
		sleep(10)

		try:
			banner = self.driver.find_element(By.XPATH,'//div[@role="banner"]')
			self.delete_element(banner)
		except: pass

		conn = sqlite3.connect('userdata/clicked_links.db')
		c = conn.cursor()

		counter = 0
		last_element = ''
		while True:
			if QUIT_DRIVER.value: conn.close();return
			if STOP_WATCHING.value: conn.close();return
			article_elements = self.driver.find_elements(By.XPATH,"//div[@class='x1lliihq']")
			if last_element != '':
				indx = article_elements.index(last_element)
				article_elements = article_elements[indx+1:]

			if article_elements == []:
				break

			for article_element in article_elements:
				if counter == 20:
					if QUIT_DRIVER.value: conn.close();return
					if STOP_WATCHING.value: conn.close();return
					conn.close()
					return
				last_element = article_element
				article_element.location_once_scrolled_into_view
				sleep(10)
				sponsored = False

				try:
					sponsored = article_element.find_element(By.XPATH,'.//a[@aria-label="Sponsored"]')
					sponsored = True
				except:
					pass

				if sponsored:
					try:
						link_element = article_element.find_element(By.XPATH,'.//a[@rel="nofollow noopener"]')
						link_element.location_once_scrolled_into_view
						link = link_element.get_attribute('href')
						link = link.split('fbclid')[0]
						c.execute('INSERT INTO clicked_links (post_URL) \
								VALUES ("' + aes_encrypt(link, key) + '")');
						conn.commit()
						write_log(get_date()+": Clicked link "+link[:140]+"..." ,key)
						action = ActionChains(self.driver)
						action\
							.move_to_element(link_element)\
							.key_down(Keys.CONTROL)\
							.click(link_element)\
							.key_up(Keys.CONTROL)\
							.perform()
						del action
						sleep(5)
						self.driver.switch_to.window(self.driver.window_handles[-1])
						sleep(1)
						if len(self.driver.window_handles) == 2:
							self.driver.close()
							self.driver.switch_to.window(self.driver.window_handles[-1])
						if QUIT_DRIVER.value: return
						sleep(1)
					except: pass

				if QUIT_DRIVER.value: conn.close();return
				if STOP_WATCHING.value: conn.close();return
				if counter % 5 == 0:
					#try:
						ad_elements = self.driver.find_elements(By.XPATH,'//a[@aria-label="Advertiser"]')
						for el in ad_elements:
							link = el.get_attribute('href')
							link = link.split('fbclid')[0]
							try:
								c.execute('INSERT INTO clicked_links (post_URL) \
									VALUES ("' + aes_encrypt(link, key) + '")');
								conn.commit()
								write_log(get_date()+": Clicked link "+link[:140]+"..." ,key)
								action = ActionChains(self.driver)
								action\
									.move_to_element(el)\
									.key_down(Keys.CONTROL)\
									.click(el)\
									.key_up(Keys.CONTROL)\
									.perform()
								del action
								sleep(5)
								self.driver.switch_to.window(self.driver.window_handles[-1])
								sleep(1)
								if len(self.driver.window_handles) == 2:
									self.driver.close()
									self.driver.switch_to.window(self.driver.window_handles[-1])
								if QUIT_DRIVER.value: conn.close();return
								sleep(1)
							except: pass
				if QUIT_DRIVER.value: conn.close();return
					#except:pass
				counter += 1

			sleep(random.randint(6,15))
		conn.close()


	def watch_videos(self, randtime, key):
		wait_thread = threading.Thread(target=self.wait, args=[randtime])
		wait_thread.start()

		self.click_links(key)
		#if QUIT_DRIVER.value: return
		#if STOP_WATCHING.value: return

		conn = sqlite3.connect('userdata/watched_videos.db')
		c = conn.cursor()
		keyword, _ = self.check_keyword(key)
		url = 'https://www.facebook.com/watch/search/?q=' + keyword
		self.driver.get(url)

		try: create_video_db(aes_encrypt(keyword,key))
		except sqlite3.OperationalError: pass

		sleep(5)
		#randtime = randtime - 5
		banner = self.driver.find_element(By.XPATH,'//div[@role="banner"]')
		self.delete_element(banner)

		first = self.driver.find_element(By.XPATH,"//div[@class='x1yztbdb']")
		self.delete_element(first)

		last_element = ''
		prev_video_elements = []
		n_vid = 0
		max_n_vid = random.randint(6,14)
		
		while True:
			if n_vid == max_n_vid:
				write_log(get_date()+": "+'Taking a break from watching videos.',key)
				break
			if QUIT_DRIVER.value: break
			if STOP_WATCHING.value: break
			sleep(5)

			video_elements = self.driver.find_elements(By.XPATH,"//div[@class='x1yztbdb']")
			if prev_video_elements == video_elements:
				write_log(get_date()+": "+'No more videos to watch',key)
				break
			prev_video_elements = video_elements
			
			if last_element != '':
				try:
					indx = video_elements.index(last_element)
					video_elements = video_elements[indx+1:]
				except ValueError:
					self.driver.refresh()
					sleep(5)
					last_element = ''
					prev_video_elements = []
					no_log = False
					continue

			for video_element in video_elements:
				if n_vid == max_n_vid:
					break
				if QUIT_DRIVER.value: break
				if STOP_WATCHING.value: break
				last_element = video_element

				try:
					video_element.location_once_scrolled_into_view
					links = video_element.find_elements(By.XPATH,".//a[@role='link']")
					video_box = video_element.find_element(By.XPATH,".//span[@class='x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1tu3fi x3x7a5m x1nxh6w3 x1sibtaa x1s688f x17z8epw']")
				except:
					continue

				video_length = video_box.text
				if video_length == 'LIVE':
					continue

				post_url = links[0].get_attribute('href')
				post_url = post_url.split('&external_log_id')[0]
				page_url = links[1].get_attribute('href')

				try:
					c.execute('INSERT INTO "'+aes_encrypt(keyword,key)+'" (post_URL, page_URL, time) \
								VALUES ("' + aes_encrypt(post_url, key) + '","' + aes_encrypt(page_url, key) + '","'+ get_date() + '")');
					conn.commit()
					write_log(get_date()+": Watching video for {} (mm:ss)\n      Post: {}\n      Page: {}".format(video_length, post_url, page_url), key)
				except sqlite3.IntegrityError:
					continue

				video_box.click()
				sleep(3)
				post_url = self.driver.current_url
				
				v_len = video_length.split(':')
				if len(v_len) == 2:
					delta = timedelta(minutes=int(v_len[-2]), seconds=int(v_len[-1]))
				elif len(v_len) == 3:
					delta = timedelta(hours=int(v_len[-3]) ,minutes=int(v_len[-2]), seconds=int(v_len[-1]))
				watch_time = 5 + delta.total_seconds()

				sleep(int(watch_time/2))
				decide_like = bool(random.randint(0,1))
				if decide_like:
					try:
						like_element = self.driver.find_element(By.XPATH, './/div[@aria-label="Like"]')
						like_element.click()
						write_log(get_date()+": "+'Liked video.',key)
					except NoSuchElementException:
						print(get_date()+": "+"Video already liked.")

				sleep(int(watch_time/2))

				if QUIT_DRIVER.value: break
				if STOP_WATCHING.value: break

				self.driver.back()
				n_vid += 1
				sleep(3)

		conn.close()
		wait_thread.join()
		STOP_WATCHING.value = False

	def pages_based_on_keyword(self, key):
		# Get current keyword and how many times it was used
		keyword, usage_number = self.check_keyword(key)
		enc_keyword = aes_encrypt(keyword, key)

		# See if db exists. Otherwise, create it 
		conn = sqlite3.connect('userdata/pages.db')
		c = conn.cursor()
		try:
			c.execute("SELECT category FROM categories")
		except sqlite3.OperationalError:
			create_categ_table()
		# then, get the keywords from the db
		keywords_in_db = c.fetchall()

		# Select URLs of respective keyword
		if (enc_keyword,) in keywords_in_db:
			c.execute('SELECT ID FROM categories WHERE category IS "'+enc_keyword+'"')
			ID = c.fetchall()
			c.execute('SELECT URL FROM pages WHERE categID IS '+str(ID[0][0]))
			urls = c.fetchall()
			conn.close()
			# Generate new keyword if done with urls from db
			nr_of_urls = len(urls)
			if usage_number >= nr_of_urls - 1:
				keyword = self.gen_keyword(keyword, key)
				enc_keyword = aes_encrypt(keyword, key)
		#if QUIT_DRIVER.value: return

		# Add new keyword to db
		if (enc_keyword,) not in keywords_in_db:
			categID = new_keyword(enc_keyword)
			search_url = 'https://www.facebook.com/search/pages?q=' + keyword
			write_log(get_date()+": "+"GET: "+ search_url,key)
			self.driver.get(search_url)
			sleep(3)
			#if QUIT_DRIVER.value: return
			# GET FB URLs based on keyword
			page_urls = self.select_pages(categID, key)
			#if QUIT_DRIVER.value: return
			info = "Pages selected for keyword '{}':".format(keyword)
			write_log(get_date()+": "+info,key)
			for page_url in page_urls:
				write_log(get_date()+": "+"   "+ aes_decrypt(page_url[0],key),key)
			# Save URLs to db
			conn = sqlite3.connect('userdata/pages.db')
			c = conn.cursor()
			c.executemany('INSERT INTO pages (URL, categID) \
				  		   VALUES (?, ?)', page_urls);
			conn.commit()
			conn.close()

		return enc_keyword


	def load_more(self, n, sec):
		# Scroll down n times to load more elements
		for i in range(n):
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			sleep(sec)
			if QUIT_DRIVER.value: break

	def login(self, key):
		# Log in to Facebook
		write_log(get_date()+": "+"Logging in...",key)
		self.driver.get("https://www.facebook.com")
		self.driver.find_element(By.XPATH,"//button[@data-cookiebanner='accept_button']").click()
		sleep(1)
		if QUIT_DRIVER.value: return
		# Decrypt password
		with open(os.getcwd()+'/'+'.saved_data','r') as f:
			text = f.read()
			text = text.split('\n')
			email = aes_decrypt(text[0],key)
			encp = text[1]
		password = aes_decrypt(encp, key)
		# Input email and password, then click Log In button.
		self.driver.find_element(By.NAME,"email").send_keys(email)
		self.driver.find_element(By.NAME,"pass").send_keys(password)
		self.driver.find_element(By.XPATH,"//*[text() = 'Log In']").click()
		sleep(3)

	def select_pages(self, categID, key):
		self.load_more(NORMAL_LOAD_AMMOUNT, 3)
		urls = self.driver.find_elements(By.TAG_NAME,'a')
		urls = [a.get_attribute('href') for a in urls]
		return_urls = []
		for url in urls:
			if url.endswith('?__tn__=%3C'):
				enc_url = aes_encrypt(url.split('?__tn__=%3C')[0], key)
				return_urls.append((enc_url,categID))

		rand_number = random.randint(8,15)
		return return_urls[:rand_number]


	def delete_element(self, element):
		self.driver.execute_script("""var element = arguments[0];
								element.parentNode.removeChild(element);
								""", element)

	def delete_banners(self):
		try:
			banner = self.driver.find_element(By.XPATH, '//div[@style="top: 56px;"]')
			self.delete_element(banner)
		except: pass
		try:
			banner = self.driver.find_element(By.XPATH, '//div[@style="top: 56px; z-index: 1;"]')
			self.delete_element(banner)
		except: pass
		try:
			banner = self.driver.find_element(By.XPATH, '//div[@style="top:56px;z-index:"]')
			self.delete_element(banner)
		except: pass
		try:
			banner = self.driver.find_element(By.XPATH, '//div[@style="top: 56px; z-index: auto;"]')
			self.delete_element(banner)
		except: pass

	def like_page(self):
		try:
			main_element = self.driver.find_element(By.XPATH, '//div[@style="top:56px;z-index:"]//div[@aria-label="Like"]')
			main_element.click()
		except: pass
		try:
			main_element = self.driver.find_element(By.XPATH, '//div[@style="top: 56px; z-index: 1;"]//div[@aria-label="Like"]')
			main_element.click()
		except: pass
		try:
			main_element = self.driver.find_element(By.XPATH, '//div[@style="top: 56px; z-index: auto;"]//div[@aria-label="Like"]')
			main_element.click()
		except: pass
		try:
			main_element = self.driver.find_element(By.XPATH, '//div[@style="top:56px;z-index:"]//div[@aria-label="Follow"]')
			main_element.click()
		except: pass
		try:
			main_element = self.driver.find_element(By.XPATH, '//div[@style="top: 56px; z-index: 1;"]//div[@aria-label="Follow"]')
			main_element.click()
		except: pass
		try:
			main_element = self.driver.find_element(By.XPATH, '//div[@style="top: 56px; z-index: auto;"]//div[@aria-label="Follow"]')
			main_element.click()
		except: pass
		
		try:
			main_element = self.driver.find_element(By.XPATH, '//div[@aria-label="Follow"]')
			main_element.click()
		except: pass
		

	def like_rand(self, pagename, eff_privacy, key):
		sleep(2)
		amount_of_likes = 0

		# Like page
		self.like_page()

		# Delete banner elements
		self.delete_banners()
		banner_2 = self.driver.find_element(By.XPATH, '//div[@role="banner"]')
		self.delete_element(banner_2)

		random_break = random.randint(6,14)

		# Connect to database
		conn = sqlite3.connect('userdata/likes.db')
		c = conn.cursor()

		# Randomly like posts in an infinite while loop until broken
		last_element = ''
		prev_article_elements = []
		write_log(get_date()+": "+'Start liking posts',key)
		while True:
			if QUIT_DRIVER.value: break
			# Find article elements
			article_elements = self.driver.find_elements(By.XPATH, "//div[@class='x1ja2u2z xh8yej3 x1n2onr6 x1yztbdb']")

			if article_elements == prev_article_elements:
				write_log(get_date()+": "+'No more posts on this page',key)
				break
			prev_article_elements = article_elements

			if last_element != '':
				indx = article_elements.index(last_element)
				article_elements = article_elements[indx+1:]
			
			# Go through every element
			for article_element in article_elements:
				if QUIT_DRIVER.value: break
				article_element.location_once_scrolled_into_view
				if last_element == '':
					self.delete_banners()
				last_element = article_element
				try:
					check_if_liked = article_element.find_element(By.XPATH, './/div[@aria-label="Remove Like"]')
					sleep(random.randint(3,7))
					if QUIT_DRIVER.value: break
					continue
				except NoSuchElementException:
					pass
				sleep(random.randint(3,20))
				if QUIT_DRIVER.value: break
				try:
					decide_like = bool(random.randint(0,1))
					if decide_like:
						# Find and focus a post element that uncovers the post url.
						link_element = article_element.find_element(By.XPATH, './/span[@class="x4k7w5x x1h91t0o x1h9r5lt x1jfb8zj xv2umb2 x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1qrby5j"]')
						action = ActionChains(self.driver)
						action.move_to_element(link_element).perform()
						if QUIT_DRIVER.value: break
						sleep(3)
						try:
							dots_elemn = article_element.find_element(By.XPATH, './/div[@class="xqcrz7y x78zum5 x1qx5ct2 x1y1aw1k x1sxyh0 xwib8y2 xurb0ha xw4jnvo"]')
							action.move_to_element(dots_elemn).perform()
						except: pass
						sleep(2)
						if QUIT_DRIVER.value: break
						post_url = link_element.find_element(By.XPATH, './/a[@role="link"]').get_attribute('href')
						post_url = post_url.split('__cft__')[0]

						# Like post
						like_element = article_element.find_element(By.XPATH, './/div[@aria-label="Like"]')
						like_element.location_once_scrolled_into_view
						like_element.click()
						amount_of_likes += 1

						# Save post to database
						c.execute('INSERT INTO "' + aes_encrypt(pagename,key) + '" (post, time) \
								VALUES ("' + aes_encrypt(post_url,key) + '","' + get_date() + '")');
						conn.commit()
						write_log(get_date()+": "+"Liked {} post on page {}".format(post_url, pagename),key)
						sleep(random.randint(1,5))
						if QUIT_DRIVER.value: break
						del action
				except Exception as e:
					print(get_date()+":","DEBUG:", e)

			if amount_of_likes > random_break:
				write_log(get_date()+": "+"Random loop break",key)
				break
			sleep(random.randint(3,10))
			if QUIT_DRIVER.value: break

		conn.close()

	def take_screenshot(self, ):
		# Take a browser screenshot every second
		while not QUIT_DRIVER.value:
			#if not WAITING_LONG.value:
			try:self.driver.save_screenshot(os.getcwd()+'/'+".screenshot.png")
			except:pass
			sleep(1)
		
	def quit_bot(self, thread_1 = None, thread_2 = None):
		# Exit webdriver
		self.driver.quit()
		if thread_1 != None:
			thread_1.join()
		if thread_2 != None:
			thread_2.join()

#########################################################################################################################
class Enter_New_Keyword(tk.Tk):

	def __init__(self, parent, key):
		tk.Tk.__init__(self,parent)
		self.parent = parent
		# Window options
		self.protocol('WM_DELETE_WINDOW', self.close)
		self.grid()
		Keyword_Info = "Enter a new seed keyword and press the\nContinue button. The program will exit\nand you will have to relaunch it."
		tk.Label(self, text=Keyword_Info).grid(row=0, columnspan=3)

		# Input new keyword
		tk.Label(self, text="New seed keyword: ").grid(row=1, column=0)
		self.Keyword = tk.Entry(self)
		self.Keyword.grid(row=1, column=1, columnspan=2,sticky='we')

		# Continue button
		self.OK_button = tk.Button(self, text="Continue", command=lambda: self.reset_keyword(key)).grid(row=2, column=0,columnspan=3)

	def reset_keyword(self,key):
		word = self.Keyword.get()
		if word != '':
			filepath = os.getcwd()+'/'+'.saved_data'
			with open(filepath, "r") as f1:
			   text = f1.read()
			text = text.split('\n')
			text[2] = aes_encrypt(word + '|' + str(0),key)
			timestamp = get_date()
			new_hmac = b64encode(Hash(b64encode(key).decode('utf-8') + timestamp + text[2])).decode('utf-8')
			text[6] = new_hmac
			text[7] = timestamp
			text = '\n'.join(text)
			with open(filepath, "w") as f2:
				f2.write(text)
			NEW_SEED.value = True
			self.close()

	def close(self):
		self.destroy()

class Userinterface(tk.Frame):

	def __init__(self, parent, key, *args, **kwargs):
		self.BOT_started = False
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.mainwindow = parent

		# Window options
		self.mainwindow.title("MetaPriv")
		self.mainwindow.option_add('*tearOff', 'FALSE')
		self.mainwindow.protocol('WM_DELETE_WINDOW', self.close)
		self.mainwindow.grid_rowconfigure(0, weight=1)
		self.mainwindow.grid_rowconfigure(1, weight=1)
		self.mainwindow.grid_rowconfigure(2, weight=1)
		self.mainwindow.grid_rowconfigure(3, weight=1)
		self.mainwindow.grid_columnconfigure(0, weight=1)
		self.mainwindow.grid_columnconfigure(1, weight=1)
		self.mainwindow.grid_columnconfigure(2, weight=1)
		
		########### Canvas ###########
		self.canvas = tk.Canvas(self.mainwindow, width=1400, height=650, background=W)
		self.canvas.grid(row=1, column=0,columnspan=3)

		########### Slider ###########
		self.eff_privacy = tk.DoubleVar()
		tk.Label(self.mainwindow, text=INFO_TEXT, background=W,
			font=('TkFixedFont', 15, '')).grid(row=1, column=1,sticky='n')
		self.slider = tk.Scale(self.mainwindow,from_=10,to=60,orient='horizontal', background=W,
			variable=self.eff_privacy,tickinterval=10,sliderlength=20,resolution=10,length=1000,width=18,
			label='Posts per day (max):',font=15,troughcolor='grey',highlightbackground=W)#
		self.slider.grid(column=0,row=1,sticky='sew', columnspan=3)

		########### Start button ###########
		self.start_button = tk.Button(self.mainwindow, text="Start Bot Process", command= lambda: self.strt(key),
			font=10, background=W)
		self.start_button.grid(row=3,column=2,sticky='ew')
		
		########### Logs ###########
		self.grid(column=0, row=2, sticky='ew', columnspan=3)
		self.textbox = ScrolledText.ScrolledText(self,state='disabled', height=8, width=173, background='black')
		self.textbox.configure(font=('TkFixedFont', 10, 'bold'),foreground='green')
		self.textbox.grid(column=0, row=2, sticky='w', columnspan=3)

		########### Stats button ###########
		self.stats_button = tk.Button(self.mainwindow, text="Keyword Statistics", command= lambda: self.stats_window(key),
			font=10, background=W)
		self.stats_button.grid(row=3,column=1,sticky='ew')

		########### Keyword button ###########
		self.kwrd_button = tk.Button(self.mainwindow, text="Reset Seed Keyword", command= lambda: self.reset_seed_keyword(key),
			font=10, background=W)
		self.kwrd_button.grid(row=3,column=0,sticky='ew')

	def reset_seed_keyword(self,key):
		new_seed = Enter_New_Keyword(None,key)
		new_seed.title("New seed keyword")
		new_seed.resizable(False, False)
		new_seed.mainloop()

	def stats_window(self, key):
		stats = tk.Tk()
		stats.resizable(False, False)
		StatsWindow(stats,key)
		stats.mainloop()
		
	def get_last_log(self, key):
		# Get last line in bot_logs.log
		with open(os.getcwd()+'/'+'bot_logs.log','rb') as f:
			try:
				f.seek(-2, os.SEEK_END)
				while f.read(1) != b'\n':
					f.seek(-2, os.SEEK_CUR)
			except OSError:
				f.seek(0)
			last_line = f.readline().decode()
			last_line = aes_decrypt(last_line, key)
		return last_line

	def update_ui(self, key):
		# Update logs
		last_log = self.get_last_log(key)
		if last_log != self.previous_last_log:
			self.textbox.configure(state='normal')
			self.textbox.insert(tk.END, last_log+"\n")
			self.textbox.configure(state='disabled')
		self.previous_last_log = last_log
		self.textbox.yview(tk.END)
		# Update screenshot
		try:
			photo = tk.PhotoImage(file=os.getcwd()+'/'+".screenshot.png")
			self.screeshot_label.image = photo
			self.screeshot_label.config(image=photo)
			self.mainwindow.update_idletasks()
		except:
			#print("Image error")
			pass
		# Recursion
		self.mainwindow.after(2000,self.update_ui, key)

	def strt(self,key):
		# Get inputs
		self.textbox.configure(state='normal')
		self.textbox.insert(tk.END, get_date()+": "+"Starting bot...\n")
		self.textbox.configure(state='disabled')
		priv = int(self.eff_privacy.get() - 10)
		# Start BOT on different core
		self.BOT = BOT()
		self.bot_process = mp.Process(target=self.BOT.start_bot,args=[priv, key])
		self.bot_process.start()
		self.textbox.configure(state='normal')
		self.textbox.insert(tk.END, get_date()+": "+"Bot process started...\n")
		self.textbox.configure(state='disabled')
		self.BOT_started = True
		# Get the last log
		try: self.previous_last_log = self.get_last_log(key)
		except FileNotFoundError: sleep(3); self.previous_last_log = self.get_last_log(key)
		# Disable inputs
		self.start_button["state"] = "disabled"
		self.slider["state"] = "disabled"
		sleep(5)
		########### Screenshot ###########
		self.screeshot_label = tk.Label(self.mainwindow)
		self.screeshot_label.grid(row=1, column=0,columnspan=3)
		# Start recursive update
		self.mainwindow.after(0,self.update_ui, key)
		
	def close(self):
		self.mainwindow.destroy()
		BREAK_SLEEP.value = True
		if self.BOT_started:
			QUIT_DRIVER.value = True
			self.bot_process.join()
			try:
				os.remove(".screenshot.png")
			except FileNotFoundError:
				pass
		
#########################################################################################################################

def sleep(seconds):#, watching_video = False):
	time = 0
	net_up = 1
	while True:
		# Computation time. On average the waiting time == seconds parameter
		if CHECK_NET.value:
			response = os.system("ping -c 1 -w2 " + "www.google.com" + " > /dev/null 2>&1")
			if response != 0:
				if net_up:
			  		print (get_date()+": "+"No internet.")
				Sleep(1)
				net_up = 0
				continue
		net_up = 1
		Sleep(1-0.003)
		time += 1
		if BREAK_SLEEP.value:
			break
		if STOP_WATCHING.value:
			break
		if time == seconds:
			break

def new_page(pagename):
	# Add a new page to database
	conn = sqlite3.connect('userdata/likes.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE "{}"
	             ([post] text PRIMARY KEY,
	              [time] date)'''.format(pagename))
	conn.commit()
	conn.close()

def new_keyword(keyword):
	# Add a new keyword to database
	conn = sqlite3.connect('userdata/pages.db')
	c = conn.cursor()
	c.execute('INSERT INTO categories (category) \
			  		   VALUES (?)', [keyword])
	conn.commit()
	ID = c.lastrowid
	conn.close()
	return ID

def create_categ_table():
	# Create pages database to store page urls based on a keyword
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

def create_video_db(keyword):
	conn = sqlite3.connect('userdata/watched_videos.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE "{}"
	             ([post_URL] text PRIMARY KEY,
	              [page_URL] text,
	              [time] date)'''.format(keyword))
	conn.commit()
	conn.close()

def create_clicked_links_db():
	conn = sqlite3.connect('userdata/clicked_links.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE clicked_links
	             ([post_URL] text PRIMARY KEY,
	              [time] date)''')
	conn.commit()
	conn.close()

def rand_dist(eff_privacy):
	# 
	max_time = 70/eff_privacy * 60 * 60
	time = random.randint(10,max_time)
	return time
	'''
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
	'''


def rand_fb_site():
	# Return a random FB site so GET while waiting
	marketplace = 'https://www.facebook.com/marketplace/?ref=bookmark'
	notifications = "https://www.facebook.com/notifications"
	friends = 'https://www.facebook.com/friends'
	settings = 'https://www.facebook.com/settings/?tab=account'
	welcome_pg = 'https://www.facebook.com/?sk=welcome'
	sites = [marketplace,notifications,friends,settings,welcome_pg]
	return sites[random.randint(0,4)]

def write_log(text,key):
	# Write and print logs
	print(text)
	with open(os.getcwd()+'/'+"bot_logs.log",'a') as f:
		f.write('\n'+aes_encrypt(text,key))

def get_date():
	# Get formatted date for logs
	now = datetime.now()
	formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
	return formatted_date

def main():
	# Check if program was launched before
	if not os.path.isfile(os.getcwd()+'/'+'.saved_data'):
		first_launch = First_launch_UI()
		first_launch.start()
		key = first_launch.h_password
		del first_launch
	else: # If yes, prompt password
		check_pass = Enter_Password_UI(None)
		check_pass.title("Enter password")
		check_pass.resizable(False, False)
		check_pass.mainloop()
		key = check_pass.h_password
		check_pass.stop()
		del check_pass

	# Start main UI
	root = tk.Tk()
	root.resizable(False, False)
	Userinterface(root,key)
	root.mainloop()
	
main()
