# partial imports
from PIL import ImageTk,Image 
# full imports
import tkinter as tk
import tkinter.scrolledtext as ScrolledText
import multiprocessing as mp
import os
import random
import getpass
import threading
import sqlite3
import logging
import ctypes

#import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from time import sleep as Sleep
from datetime import datetime, timedelta


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
NORMAL_LOAD_AMMOUNT = 3
ONE_HOUR = 3600
quit_driver = mp.Value('b', False)
BREAK_SLEEP = False

class BOT:

	def load_more(self, n, sec):
		# Scroll down n times to load more elements
		for i in range(n):
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			sleep(sec)

	def login(self, ):
		write_log(get_date()+": "+"Logging in")
		self.driver.get("https://www.facebook.com")
		self.driver.find_element(By.XPATH,"//*[text() = 'Accept All']").click()
		sleep(1)
		email = input("Enter email: ")
		password = getpass.getpass("Enter password: ")
		self.driver.find_element(By.NAME,"email").send_keys(email)
		self.driver.find_element(By.NAME,"pass").send_keys(password)
		self.driver.find_element(By.XPATH,"//*[text() = 'log In']").click()

	def analize_weekly_liked_posts(self, ):
		self.driver.get("https://www.facebook.com/100065228954924/allactivity?category_key=ALL")
		while True:
			self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
			days = self.driver.find_elements(By.XPATH, "//div[@class='kvgmc6g5 sj5x9vvc sjgh65i0 l82x9zwi uo3d90p7 pw54ja7n ue3kfks5 hybvsw6c']")
			if len(days) > 8:
				break
			sleep(5)

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
		load_more(NORMAL_LOAD_AMMOUNT, 3)
		urls = self.driver.find_elements_by_tag_name('a')
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
			os.mkdir("userdata/"+pagename_short)
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

		# Connect to database
		conn = sqlite3.connect('userdata/likes.db')
		c = conn.cursor()

		# Randomly like posts
		last_element = ''
		while not quit_driver.value:
			#self.update_ui()
			
			article_elements = self.driver.find_elements(By.XPATH, "//div[@class='lzcic4wl']")
			if last_element != '':
				indx = article_elements.index(last_element)
				article_elements = article_elements[indx+1:]

			# Go through every element
			for article_element in article_elements:
				if quit_driver.value: break
				last_element = article_element
				article_element.location_once_scrolled_into_view
				try:
					check_if_liked = article_element.find_element(By.XPATH, './/div[@aria-label="Remove Like"]')
					if quit_driver.value: break
					sleep(random.randint(3,7))
					continue
				except NoSuchElementException:
					pass
				if quit_driver.value: break
				sleep(3)
				#self.update_ui()
				sleep(random.randint(0,17))
				try:
					decide_like = bool(random.randint(0,1))
					if decide_like:
						link_element = article_element.find_element(By.XPATH, './/a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]')

						action = ActionChains(self.driver)
						try: action.move_to_element(link_element).perform()
						except: pass
						if quit_driver.value: break
						sleep(1)
						action.move_by_offset(500, 0).perform()
						sleep(2)
						if quit_driver.value: break
						#self.update_ui()

						post_url = article_element.find_element(By.XPATH, './/a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]').get_attribute('href')
						post_url = post_url.split('__cft__')[0]
					
						# Save screenshot
						data = article_element.screenshot_as_png
						with open("userdata/"+pagename_short+"/"+get_date()+".png",'wb') as f:
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
						if quit_driver.value: break
						sleep(random.randint(1,5))
						#self.update_ui()
						del action
				except Exception as e:
					write_log(get_date()+": "+e)

			random_addition = int(avg_amount_of_likes_per_day*0.2)
			random_break = random.randint(-random_addition,random_addition)
			# avg pages per day == 7
			if amount_of_likes > ((avg_amount_of_likes_per_day + random_break) * (eff_privacy/0.5)) / 7:
				write_log(get_date()+": "+"Random loop break")
				break
			if quit_driver.value: break
			sleep(random.randint(3,10))

		conn.close()

	def worker(self, ):
		while not quit_driver.value:
			self.driver.save_screenshot(".screenshot.png")
			sleep(1)

	def start_bot(self, eff_privacy):
		#global driver
		#global log

		#quit_driver.value = False
		#log = Log()

		#info
		
		profile_path = '.mozilla/firefox/' #'/home/'+ os.getlogin() + 
		try:
			profile_path += [a for a in os.listdir(profile_path) if a.endswith('.default-esr')][0]
		except IndexError:
			profile_path += [a for a in os.listdir(profile_path) if a.endswith('.default-release')][0]
		#fx_prof = webdriver.FirefoxProfile(profile_path)

		#exec_path = input("Enter geckodriver executable path:")
		#exec_path = '/home/'+ os.getlogin() + '/Downloads/geckodriver/geckodriver'
		#ser = Service(exec_path)

		#keyword = input("Enter search keyword: ")
		#keyword = keyword.replace(" ","+")
		#eff_privacy = int(input("Enter desired privacy (1-100): "))
		keyword = "bodybuilding"
		eff_privacy = eff_privacy / 100
		
		try: 
			os.mkdir("userdata")
		except FileExistsError:
			pass
		
		fx_options = Options()
		fx_options.add_argument("--profile")
		fx_options.add_argument(profile_path)
		fx_options.add_argument("--headless")
		self.driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options = fx_options)
		self.driver.set_window_size(1280,1024)
		t1 = threading.Thread(target=self.worker, args=[])
		t1.start()

		#t2 = threading.Thread(target=self.worker2, args=[])
		#t2.start()

		if os.path.isfile('userdata/avg_daily_posts'):
			with open('userdata/avg_daily_posts','r') as f:
				avg_amount_of_likes_per_day = int(f.read())
		else:
			avg_amount_of_likes_per_day = self.analize_weekly_liked_posts()
			with open('userdata/avg_daily_posts','w') as f:
				f.write(str(avg_amount_of_likes_per_day))
		

		# get tables from database
		conn = sqlite3.connect('userdata/pages.db')
		c = conn.cursor()

		try:
			c.execute("SELECT category FROM categories")
		except sqlite3.OperationalError:
			self.create_categ_table()
		keywords_in_db = c.fetchall()
		conn.close()

		rand_ste = rand_fb_site()
		self.driver.get(rand_ste)
		sleep(2)
		#self.update_ui()
		sleep(3)

		if (keyword,) not in keywords_in_db:
			categID = new_keyword(keyword)
			search_url = 'https://www.facebook.com/search/pages?q=' + keyword
			#print("GET: "+ search_url)
			write_log(get_date()+": "+"GET: "+ search_url)
			self.driver.get(search_url)
			sleep(2)
			#self.update_ui()
			sleep(3)

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
		random.shuffle(urls)

		# get tables from database
		conn = sqlite3.connect('userdata/likes.db')
		c = conn.cursor()
		c.execute("SELECT name FROM sqlite_master WHERE type='table';")
		urls_in_db = c.fetchall()
		conn.close()

		#driver.save_screenshot("screenshot.png")
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
			write_log(get_date()+": "+"GET: "+ url)
			self.driver.get(url)
			if quit_driver.value: break
			sleep(10)

			if ((url,)) in urls_in_db:
				self.like_rand(url, False, avg_amount_of_likes_per_day, eff_privacy)
			else:
				new_page(url)
				self.like_rand(url, True, avg_amount_of_likes_per_day, eff_privacy)
			
			if quit_driver.value:
				break
			rand_site = rand_fb_site()
			self.driver.get(rand_site)
			# wait between 10s and 10 hours
			randtime = rand_dist()
			sleep(2)
			
			time_formatted = str(timedelta(seconds = randtime))
			write_log(get_date()+": "+"Wait for "+ time_formatted + " (hh:mm:ss)")
			if quit_driver.value: break
			sleep(randtime)
			#counter += 1
		#t2.join()
		self.driver.quit()
		t1.join()

###########################################################################

class Userinterface(tk.Frame):

	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.mainwindow = parent
		self.mainwindow.title("FbObfusc")

		self.mainwindow.option_add('*tearOff', 'FALSE')
		self.mainwindow.protocol('WM_DELETE_WINDOW', self.close)
		
		self.BOT_started = False

		########### Slider ###########
		self.eff_privacy = tk.DoubleVar()
		slider_label = tk.Label(self.mainwindow,text='Effective Privacy (0-100):')
		slider_label.grid(column=0,row=0,sticky='w')
		slider = tk.Scale(self.mainwindow,from_=10,to=100,orient='horizontal',
			variable=self.eff_privacy,tickinterval=10,sliderlength=20,resolution=5)
		slider.set(55)
		slider.grid(column=1,row=0,sticky='we')
		########### Start button ###########
		self.start_button = tk.Button(self.mainwindow, text="Start", command=self.strt)
		self.start_button.grid(row=0,column=2,sticky='e')
		########### Screenshot ###########
		image = Image.open("Start.png")
		resized_image = image.resize((800, 600))
		photo = ImageTk.PhotoImage(resized_image)
		self.screeshot_label = tk.Label(self.mainwindow, image = photo)
		self.screeshot_label.image = photo
		self.screeshot_label.grid(row=1, column=0,columnspan=3)
		########### Logs ###########
		self.grid(column=0, row=3, sticky='ew', columnspan=3)
		self.t = ScrolledText.ScrolledText(self,state='disabled', height=12, width=112)
		self.t.configure(font='TkFixedFont')
		self.t.grid(column=0, row=3, sticky='w', columnspan=3)
		
	def get_last_log(self):
		with open('bot_logs.log','rb') as f:
			try:
				f.seek(-2, os.SEEK_END)
				while f.read(1) != b'\n':
					f.seek(-2, os.SEEK_CUR)
			except OSError:
				f.seek(0)
			last_line = f.readline().decode()
		return last_line

	def update_ui(self):
		last_log = self.get_last_log()
		if last_log != self.previous_last_log:
			self.t.configure(state='normal')
			self.t.insert(tk.END, last_log)
			self.t.configure(state='disabled')
		self.previous_last_log = last_log
		self.t.yview(tk.END)
		try:
			image = Image.open(".screenshot.png")
			resized_image = image.resize((800, 600))
			photo = ImageTk.PhotoImage(resized_image)
			self.screeshot_label.image = photo
			self.screeshot_label.config(image=photo)
			self.mainwindow.update_idletasks()
		except:
			#print("Image error")
			pass
		self.mainwindow.after(2000,self.update_ui)

	def strt(self):
		priv = int(self.eff_privacy.get())
		self.BOT = BOT()
		self.bot_process = mp.Process(target=self.str_BOT,args=[priv])
		self.bot_process.start()
		self.previous_last_log = self.get_last_log()
		self.mainwindow.after(2000,self.update_ui)
		self.BOT_started = True

	def str_BOT(self, priv):
		self.BOT.start_bot(priv)

	def openNewWindow(self):
		self.newWindow = tk.Toplevel(self.mainwindow)
		self.newWindow.title("New Window")
		self.newWindow.geometry("200x200")
		tk.Label(self.newWindow,text ="Closing application").pack()
		
	def close(self):
		BREAK_SLEEP = True
		if self.BOT_started:
			quit_driver_signal()
			self.bot_process.join()
			print("Processes joined")
		self.mainwindow.destroy()
		
def quit_driver_signal(): quit_driver.value = True

def write_log(text):
	print(text)
	with open("bot_logs.log",'a') as f:
		f.write(text+'\n')

def sleep(seconds):
	time = 0
	while True:
		Sleep(1)
		time += 1
		if BREAK_SLEEP:
			break
		if time == seconds:
			break

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

def get_date():
	now = datetime.now()
	formatted_date = now.strftime(DATE_FORMAT)
	return formatted_date

def main():
	root = tk.Tk()
	root.resizable(False, False)
	Userinterface(root)
	root.mainloop()
	
main()
