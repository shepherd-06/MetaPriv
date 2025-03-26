import sys
import os
import sqlite3
from crypto import aes_encrypt, aes_decrypt, Hash
from metapriv.utilities import *
from tempfile import gettempdir
from time import sleep
from random import random
import threading
from datetime import timedelta

from shutil import copytree
from base64 import b64encode

from metapriv.database_management import *


## Selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException



class BOT:
	def start_bot(self, eff_privacy, key):
		"""
			Initializes and starts the Selenium WebDriver with a specified profile and headless configuration,
			and begins a series of automated actions on a random Facebook page.

			This method sets up the logging mechanism, initializes the WebDriver based on whether a Firefox profile exists,
			and handles screenshots and cleanup through threading to ensure the operation is non-blocking.

			Parameters:
				eff_privacy (float): A parameter that could affect operational delays or decision-making in how the bot interacts.
				key (str): Encryption key used for securing logs and potentially other sensitive data managed by the bot.

			Steps:
			1. Check and log if this is the first launch.
			2. Prepare Firefox WebDriver with either a new profile or an existing one.
			3. Set browser to headless mode to ensure it runs silently without UI.
			4. Start taking screenshots in a separate thread to monitor the session.
			5. Open a random Facebook page to begin operations.
			6. Manage user data and profiles, ensuring privacy settings are respected.
			7. Optionally, clean up by closing the browser and stopping threads upon completion or error.
		"""
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
		fx_options = webdriver.FirefoxOptions()
		profile_path = os.getcwd()+'/fx_profile'
		if profile_exists:
			fx_options.add_argument("--profile")
			fx_options.add_argument(profile_path)
		fx_options.add_argument("--headless")
		fx_options.add_argument("--no-sandbox")
		fx_options.add_argument('--headless=new')
		fx_options.headless = True
		self.driver = webdriver.Firefox(options=fx_options)

		# Start
		# self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options = fx_options)
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
	
	def update_keyword(self, key, new_word = None):
		"""
		Updates or sets a keyword in the application's data file, tracking its usage count.
		
		This function handles the encrypted data storage by reading the current keyword data, updating it,
		and then writing it back to the file securely. It either increments the usage count of the existing keyword
		or initializes a new keyword with a usage count of zero if `new_word` is specified.
		
		Parameters:
			key (bytes): The encryption key used for securing the data.
			new_word (str, optional): The new keyword to set. If None, the current keyword's usage is incremented.
		
		The data file structure contains lines where:
		- Line 3 stores the encrypted keyword and its usage count.
		- Lines 7 and 8 store an HMAC and timestamp for integrity and modification tracking.
		
		The function ensures that any updates maintain data integrity by recalculating the HMAC based on the updated content.
		"""
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
		fx_options = webdriver.Options()
		fx_options.add_argument("--headless")
		driverpath = os.environ['HOME'] + "/.wdm/drivers/geckodriver/linux64/"
		versions = os.listdir(driverpath)
		versions.sort()
		version = versions[-1]
		driverpath = driverpath + version + "/geckodriver"
		# temp_driver = webdriver.Firefox(service=Service(driverpath),options = fx_options)
		temp_driver = None
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
					self.update_keyword(key)	
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

				decide_like = random.randint(0,1)
				try:
					c.execute('INSERT INTO "'+aes_encrypt(keyword,key)+'" (post_URL, page_URL, time, liked) \
								VALUES ("' + aes_encrypt(post_url, key) + '","' + aes_encrypt(page_url, key) + '","'+ get_date() + '","' + str(decide_like) + '")');
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
				
				if bool(decide_like):
					try:
						like_element = self.driver.find_element(By.XPATH, './/div[@aria-label="Like"]')
						like_element.click()
						write_log(get_date()+": "+'Liked video.',key)
					except NoSuchElementException:
						pass

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
			banner = self.driver.find_element(By.XPATH, '//div[@aria-label="Facebook"]')
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
		try:
			banner = self.driver.find_element(By.XPATH, '//div[@style="top:56px;z-index:auto"]')
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
		sleep(5)
		amount_of_likes = 0

		# Like page
		self.like_page()

		# Delete banner elements
		self.delete_banners()
		banner_2 = self.driver.find_element(By.XPATH, '//div[@role="banner"]')
		self.delete_element(banner_2)

		random_break = random.randint(8,12)

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
			article_elements = self.driver.find_elements(By.XPATH, "//div[@class='x1n2onr6 x1ja2u2z']")

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
						try: # if reel
							post_url = article_element.find_element(By.XPATH, './/a[@aria-label="Open reel in Reels Viewer"]').get_attribute('href')
							post_url = "https://www.facebook.com"+post_url.split('__cft__')[0]
						except NoSuchElementException:
							# Find and focus a post element that uncovers the post url.
							link_element = article_element.find_element(By.XPATH, './/span[@class="x4k7w5x x1h91t0o x1h9r5lt xv2umb2 x1beo9mf xaigb6o x12ejxvf x3igimt xarpa2k xedcshv x1lytzrv x1t2pt76 x7ja8zs x1qrby5j x1jfb8zj"]')
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
						try:del action
						except: pass
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
