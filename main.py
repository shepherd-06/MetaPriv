# partial imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep as Sleep
from datetime import timedelta, datetime
from tempfile import gettempdir
from shutil import copytree
# full imports
import tkinter as tk
import tkinter.scrolledtext as ScrolledText
import multiprocessing as mp
import os
import random
import getpass
import threading
import sqlite3
# imports from created files 
from firstlaunchclass import First_launch_UI
from passwordclass import Enter_Password_UI
from crypto import Hash, aes_encrypt, aes_decrypt


NORMAL_LOAD_AMMOUNT = 5
ONE_HOUR = 3600
QUIT_DRIVER = mp.Value('b', False)
BREAK_SLEEP = mp.Value('b', False)
WAITING_LONG = mp.Value('b', False)

#########################################################################################################################

class BOT:

	def start_bot(self, eff_privacy, key):
		tempdirs = []
		profile_exists = os.path.isdir(os.getcwd()+'/fx_profile')
		if not profile_exists:
			tempdirs = os.listdir(gettempdir())

		if not os.path.isfile(os.getcwd()+'/bot_logs.log'):
			text = get_date()+": "+"First launch\n"
			print(text)
			with open(os.getcwd()+'/'+"bot_logs.log", "w") as f:
				f.write(text)

		with open(os.getcwd()+'/'+'.saved_data','r') as f:
			text = f.read()
			text = text.split('\n')
			keyword = text[2]

		eff_privacy = eff_privacy / 100
		
		try: 
			os.mkdir(os.getcwd()+"/userdata")
		except FileExistsError:
			pass
		
		fx_options = Options()
		profile_path = os.getcwd()+'/fx_profile'
		if profile_exists:
			fx_options.add_argument("--profile")
			fx_options.add_argument(profile_path)
		fx_options.add_argument("--headless")
		
		self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options = fx_options)
		self.driver.set_window_size(1400,700)
		sleep(3)
		if QUIT_DRIVER.value: self.quit_bot(t1)

		t1 = threading.Thread(target=self.take_screenshot, args=[])
		t1.start()
		
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
		self.driver.get(rand_ste)
		sleep(5)
		if QUIT_DRIVER.value: self.quit_bot(t1)

		if not profile_exists:
			self.login(key)
			tempdirs_2 = os.listdir(gettempdir())
			for i in tempdirs_2:
				if i not in tempdirs:
					if 'mozprofile' in i:
						scr = gettempdir() + '/' + i
						os.remove(scr+'/lock')
						copytree(scr, profile_path)

		if os.path.isfile(os.getcwd()+'/'+'userdata/avg_daily_posts'):
			with open(os.getcwd()+'/'+'userdata/avg_daily_posts','r') as f:
				avg_amount_of_likes_per_day = int(f.read())
		else:
			avg_amount_of_likes_per_day = self.analize_weekly_liked_posts()
			with open(os.getcwd()+'/'+'userdata/avg_daily_posts','w') as f:
				f.write(str(avg_amount_of_likes_per_day))

		if (keyword,) not in keywords_in_db:
			categID = new_keyword(keyword)
			search_url = 'https://www.facebook.com/search/pages?q=' + keyword
			write_log(get_date()+": "+"GET: "+ search_url)
			self.driver.get(search_url)
			sleep(5)
			if QUIT_DRIVER.value: self.quit_bot(t1)

			page_urls = self.select_pages(categID)
			info = "Pages selected for keyword '{}':".format(keyword)
			write_log(get_date()+": "+info)
			for page_url in page_urls:
				write_log(get_date()+": "+"   "+ page_url[0])

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
		random.shuffle(urls)

		# get tables from database
		conn = sqlite3.connect('userdata/likes.db')
		c = conn.cursor()
		c.execute("SELECT name FROM sqlite_master WHERE type='table';")
		urls_in_db = c.fetchall()
		conn.close()

		for url in urls:
			url = url[1]
			write_log(get_date()+": "+"GET: "+ url)
			self.driver.get(url)
			sleep(10)
			if QUIT_DRIVER.value: break

			if ((url,)) in urls_in_db:
				self.like_rand(url, False, avg_amount_of_likes_per_day, eff_privacy)
			else:
				new_page(url)
				self.like_rand(url, True, avg_amount_of_likes_per_day, eff_privacy)
			
			rand_site = rand_fb_site()
			self.driver.get(rand_site)
			# wait between 10 s and 10 h
			randtime = rand_dist()
			if not QUIT_DRIVER.value:
				time_formatted = str(timedelta(seconds = randtime))
				write_log(get_date()+": "+"Wait for "+ time_formatted + " (hh:mm:ss)")
			sleep(2)
			if QUIT_DRIVER.value: break
			sleep(randtime, True)
			if QUIT_DRIVER.value: break

		self.quit_bot(t1)

	def load_more(self, n, sec):
		# Scroll down n times to load more elements
		for i in range(n):
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			sleep(sec)
			if QUIT_DRIVER.value: break

	def login(self, key):
		write_log(get_date()+": "+"Logging in...")
		self.driver.get("https://www.facebook.com")
		self.driver.find_element(By.XPATH,"//*[text() = 'Allow All Cookies']").click()
		sleep(1)
		if QUIT_DRIVER.value: return

		with open(os.getcwd()+'/'+'.saved_data','r') as f:
			text = f.read()
			text = text.split('\n')
			email = text[0]
			encp = text[1]
		password = aes_decrypt(encp, key)

		self.driver.find_element(By.NAME,"email").send_keys(email)
		self.driver.find_element(By.NAME,"pass").send_keys(password)
		self.driver.find_element(By.XPATH,"//*[text() = 'Log In']").click()
		sleep(3)

	def analize_weekly_liked_posts(self, ):
		write_log(get_date()+": "+"Analyzing daily Facebook interaction...")
		self.driver.get("https://www.facebook.com/100065228954924/allactivity?category_key=ALL")
		while True:
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			days = self.driver.find_elements(By.XPATH, "//div[@class='kvgmc6g5 sj5x9vvc sjgh65i0 l82x9zwi uo3d90p7 pw54ja7n ue3kfks5 hybvsw6c']")
			if len(days) > 8:
				break
			sleep(5)
			if QUIT_DRIVER.value: break

		days = days[:7]
		weekly_amount_of_likes = []
		for day in days:
			likes_per_day = day.find_elements(By.XPATH, ".//div[@class='l9j0dhe7 btwxx1t3 j83agx80']")
			likes = 0
			for like in likes_per_day:
				txt = like.find_element(By.XPATH, ".//div[@class='qzhwtbm6 knvmm38d']").text
				if 'likes' or 'reacted' in txt:
					likes += 1
			weekly_amount_of_likes.append(likes)
			likes = 0

		avg_amount_of_likes_per_day = int(sum(weekly_amount_of_likes)/len(weekly_amount_of_likes))
		return avg_amount_of_likes_per_day

	def select_pages(self, categID):
		self.load_more(NORMAL_LOAD_AMMOUNT, 3)
		urls = self.driver.find_elements(By.TAG_NAME,'a')
		urls = [a.get_attribute('href') for a in urls]
		return_urls = []
		for url in urls:
			if url.endswith('?__tn__=%3C'):
				return_urls.append((url.split('?__tn__=%3C')[0],categID))
		return return_urls

	def delete_element(self, element):
		self.driver.execute_script("""var element = arguments[0];
								element.parentNode.removeChild(element);
								""", element)


	def like_rand(self, pagename, first_visit, avg_amount_of_likes_per_day, eff_privacy):
		amount_of_likes = 0
		pagename_short = pagename.split("https://www.facebook.com/")[1]
		try: pagename_short = pagename_short.split("/")[0]
		except:pass
		# Check Chatbox element and delete it
		try:
			chatbox = self.driver.find_element(By.XPATH, '//div[starts-with(@aria-label, "Chat with")]')
			self.delete_element(chatbox)
		except NoSuchElementException: 
			pass

		if first_visit:
			# Like page
			write_log(get_date()+": "+"First visit on: "+pagename)
			os.mkdir(os.getcwd()+'/'+"userdata/"+pagename_short)
			try:
				main_element = self.driver.find_element(By.XPATH, '//div[@style="top: 56px;"]//div[@aria-label="Like"]')
				main_element.click()
			except Exception as e:
				write_log(get_date()+": "+e)

		# Delete banner elements
		try:
			banner_0 = self.driver.find_element(By.XPATH, '//div[@style="top: 56px; z-index: 1;"]')
			self.delete_element(banner_0)
		except:
			banner_1 = self.driver.find_element(By.XPATH, '//div[@style="top: 56px;"]')
			self.delete_element(banner_1)
		banner_2 = self.driver.find_element(By.XPATH, '//div[@role="banner"]')
		self.delete_element(banner_2)

		# for adding a random value between -40% and +40% to the avg_amount_of_likes_per_day variable 
		random_addition = int(avg_amount_of_likes_per_day*0.4)
		random_break = random.randint(-random_addition,random_addition)

		# Connect to database
		conn = sqlite3.connect('userdata/likes.db')
		c = conn.cursor()

		# Randomly like posts
		last_element = ''
		while True:
			if QUIT_DRIVER.value: break
			article_elements = self.driver.find_elements(By.XPATH, "//div[@class='lzcic4wl']")
			if last_element != '':
				indx = article_elements.index(last_element)
				article_elements = article_elements[indx+1:]

			# Go through every element
			for article_element in article_elements:
				if QUIT_DRIVER.value: break
				last_element = article_element
				article_element.location_once_scrolled_into_view
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
						link_element = article_element.find_element(By.XPATH, './/a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]')

						action = ActionChains(self.driver)
						try: action.move_to_element(link_element).perform()
						except: pass
						if QUIT_DRIVER.value: break
						sleep(1)
						action.move_by_offset(500, 0).perform()
						sleep(2)
						if QUIT_DRIVER.value: break
						
						post_url = article_element.find_element(By.XPATH, './/a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]').get_attribute('href')
						post_url = post_url.split('__cft__')[0]
					
						# Save screenshot
						data = article_element.screenshot_as_png
						with open(os.getcwd()+'/'+"userdata/"+pagename_short+"/"+get_date()+".png",'wb') as f:
							f.write(data)

						# Like post
						like_element = article_element.find_element(By.XPATH, './/div[@aria-label="Like"]')
						like_element.location_once_scrolled_into_view
						like_element.click()
						amount_of_likes += 1

						# Save post to database
						c.execute('INSERT INTO "' + pagename + '" (post, time) \
								VALUES ("' + post_url + '","' + get_date() + '")');
						conn.commit()
						write_log(get_date()+": "+"Liked {} post on page {}".format(post_url, pagename))
						sleep(random.randint(1,5))
						if QUIT_DRIVER.value: break
						del action
				except Exception as e:
					write_log(get_date()+": "+e)

			# avg pages per day == 7
			if amount_of_likes > ((avg_amount_of_likes_per_day + random_break) * (eff_privacy/0.5)) / 7:
				write_log(get_date()+": "+"Random loop break")
				break
			sleep(random.randint(3,10))
			if QUIT_DRIVER.value: break

		conn.close()

	def take_screenshot(self, ):
		while not QUIT_DRIVER.value:
			if not WAITING_LONG.value:
				self.driver.save_screenshot(os.getcwd()+'/'+".screenshot.png")
			sleep(1)
		
	def quit_bot(self, thread):
		self.driver.quit()
		thread.join()

#########################################################################################################################

class Userinterface(tk.Frame):

	def __init__(self, parent, key, *args, **kwargs):
		self.BOT_started = False
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.mainwindow = parent
		self.mainwindow.title("MetaPriv")

		self.mainwindow.option_add('*tearOff', 'FALSE')
		self.mainwindow.protocol('WM_DELETE_WINDOW', self.close)
		
		########### Slider ###########
		self.eff_privacy = tk.DoubleVar()
		self.slider_label = tk.Label(self.mainwindow,text='Enter desired privacy level (0-100):')
		self.slider_label.grid(column=0,row=0,sticky='w')
		self.slider = tk.Scale(self.mainwindow,from_=10,to=100,orient='horizontal',
			variable=self.eff_privacy,tickinterval=10,sliderlength=20,resolution=5)
		self.slider.set(55)
		self.slider.grid(column=1,row=0,sticky='we')

		########### Start button ###########
		self.start_button = tk.Button(self.mainwindow, text="Start", command= lambda: self.strt(key) )
		self.start_button.grid(row=0,column=2,sticky='e')

		########### Screenshot ###########
		photo = tk.PhotoImage(file=os.getcwd()+'/'+"Start.png")
		self.screeshot_label = tk.Label(self.mainwindow, image = photo)
		self.screeshot_label.image = photo
		self.screeshot_label.grid(row=1, column=0,columnspan=3)

		########### Logs ###########
		self.grid(column=0, row=3, sticky='ew', columnspan=3)
		self.textbox = ScrolledText.ScrolledText(self,state='disabled', height=12, width=198)
		self.textbox.configure(font='TkFixedFont')
		self.textbox.grid(column=0, row=3, sticky='w', columnspan=3)
		
	def get_last_log(self):
		with open(os.getcwd()+'/'+'bot_logs.log','rb') as f:
			try:
				f.seek(-2, os.SEEK_END)
				while f.read(1) != b'\n':
					f.seek(-2, os.SEEK_CUR)
			except OSError:
				f.seek(0)
			last_line = f.readline().decode()
		return last_line

	def update_ui(self):
		if not WAITING_LONG.value:
			last_log = self.get_last_log()
			if last_log != self.previous_last_log:
				self.textbox.configure(state='normal')
				self.textbox.insert(tk.END, last_log)
				self.textbox.configure(state='disabled')
			self.previous_last_log = last_log
			self.textbox.yview(tk.END)
			try:
				photo = tk.PhotoImage(file=os.getcwd()+'/'+".screenshot.png")
				self.screeshot_label.image = photo
				self.screeshot_label.config(image=photo)
				self.mainwindow.update_idletasks()
			except:
				#print("Image error")
				pass
		self.mainwindow.after(2000,self.update_ui)

	def strt(self,key):
		self.textbox.configure(state='normal')
		self.textbox.insert(tk.END, get_date()+": "+"Starting bot...\n")
		self.textbox.configure(state='disabled')
		priv = int(self.eff_privacy.get())
		self.BOT = BOT()
		self.bot_process = mp.Process(target=self.BOT.start_bot,args=[priv, key])
		self.bot_process.start()
		self.textbox.configure(state='normal')
		self.textbox.insert(tk.END, get_date()+": "+"Bot process started...\n")
		self.textbox.configure(state='disabled')
		self.BOT_started = True
		try: self.previous_last_log = self.get_last_log()
		except FileNotFoundError: sleep(3); self.previous_last_log = self.get_last_log()
		self.start_button["state"] = "disabled"
		self.slider["state"] = "disabled"
		sleep(3)
		self.mainwindow.after(2000,self.update_ui)
		
	def close(self):
		BREAK_SLEEP.value = True
		if self.BOT_started:
			QUIT_DRIVER.value = True
			self.bot_process.join()
			try:
				os.remove(".screenshot.png")
			except FileNotFoundError:
				pass
		self.mainwindow.destroy()
		
#########################################################################################################################

def sleep(seconds, long_wait = False):
	if long_wait:
		WAITING_LONG.value = True
	time = 0
	while True:
		Sleep(1-0.003)
		time += 1
		if BREAK_SLEEP.value:
			break
		if time == seconds:
			break
	if long_wait:
		WAITING_LONG.value = False

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

def write_log(text):
	print(text)
	with open(os.getcwd()+'/'+"bot_logs.log",'a') as f:
		f.write(text+'\n')

def get_date():
	now = datetime.now()
	formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
	return formatted_date

def main():
	if not os.path.isfile(os.getcwd()+'/'+'.saved_data'):
		first_launch = First_launch_UI()
		first_launch.start()
		key = first_launch.h_password
		del first_launch
	else:
		check_pass = Enter_Password_UI(None)
		check_pass.title("Enter password")
		check_pass.resizable(False, False)
		check_pass.mainloop()
		key = check_pass.h_password
		check_pass.stop()
		del check_pass

	root = tk.Tk()
	root.resizable(False, False)
	Userinterface(root,key)
	root.mainloop()
	
main()