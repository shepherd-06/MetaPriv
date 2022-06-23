# partial imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options

from time import sleep
from datetime import datetime, timedelta
# full imports
import os
import sqlite3
import random
import logging
from crypto import Hash, aes_encrypt, aes_decrypt
import getpass



DATE_FORMAT = '%Y-%m-%d_%H.%M.%S'
ONE_HOUR = 3600

def delete_element(element):
	driver.execute_script("""var element = arguments[0];
							element.parentNode.removeChild(element);
							""", element)

def get_date():
	now = datetime.now()
	formatted_date = now.strftime(DATE_FORMAT)
	return formatted_date

def create_video_feed():
	conn = sqlite3.connect('analysisdata/suggestions.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE video_feed
	             ([post_URL] text PRIMARY KEY,
	              [page_URL] text,
	              [post_time] text,
	              [description] text,
	              [time] date)''')
	conn.commit()
	conn.close()

def create_main_video_feed():
	conn = sqlite3.connect('analysisdata/suggestions.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE main_video_feed
	             ([post_URL] text PRIMARY KEY,
	              [page_URL] text,
	              [post_time] text,
	              [description] text,
	              [follow] int,
	              [time] date)''')
	conn.commit()
	conn.close()

def create_analysis_table():
	conn = sqlite3.connect('analysisdata/suggestions.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE feed
	             ([post_URL] text PRIMARY KEY,
	              [page_URL] text,
	              [post_time] text,
			[recommended] int,
	              [time] date)''')
	c.execute('''CREATE TABLE suggested_for_me
	             ([URL] text PRIMARY KEY,
			[time] date)''')

	conn.commit()
	conn.close()

def analize_feed():
	log.info("Analyzing feed")
	conn = sqlite3.connect('analysisdata/suggestions.db')
	c = conn.cursor()
	driver.get('https://www.facebook.com')

	sleep(5)
	banner = driver.find_element(By.XPATH,'//div[@role="banner"]')
	delete_element(banner)
	counter = 0
	last_element = ''
	while True:
		article_elements = driver.find_elements(By.XPATH,"//div[@class='lzcic4wl']")
		if last_element != '':
			indx = article_elements.index(last_element)
			article_elements = article_elements[indx+1:]

		if article_elements == []:
			break

		for article_element in article_elements:
			if counter == 300:
				conn.close()
				return
			counter += 1
			recommended = 0
			last_element = article_element
			article_element.location_once_scrolled_into_view
			sleep(2)
			# Save screenshot
			data = article_element.screenshot_as_png
			with open("analysisdata/f_"+get_date()+".png",'wb') as f:
				f.write(data)

			try:
				page_name = article_element.find_element(By.XPATH,".//a[@role='link']").get_attribute('href')
				page_name = page_name.split('__cft__')[0]
			except:pass
			try:
				suggestion_elements = article_element.find_elements(By.XPATH,".//div[@aria-label='Suggested for You']//a[@role='link']")
				suggestion_elements = [a.get_attribute('href') for a in suggestion_elements]
				for url in suggestion_elements:
					try:
						c.execute('INSERT INTO suggested_for_me (URL, time) \
							VALUES ("' + url + '","' + get_date() + '")');
						conn.commit()
					except sqlite3.IntegrityError:
						pass
			except Exception as e:
				pass

			try:
				link_element = article_element.find_element(By.XPATH,'.//span[@class="tojvnm2t a6sixzi8 abs2jz4q a8s20v7p t1p8iaqh k5wvi7nf q3lfd5jv pk4s997a bipmatt0 cebpdrjk qowsmv63 owwhemhu dp1hu0rb dhp61c6y iyyx5f41"]//a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]')
			except NoSuchElementException:
				continue

			action = ActionChains(driver)
			try: action.move_to_element(link_element).perform()
			except: pass

			sleep(3)
			try:
				post_date = driver.find_element(By.XPATH,'//div[@class="__fb-light-mode"]//*').text
				#<span class="d2edcug0 hpfvmrgz qv66sw1b c1et5uql b0tq1wua e9vueds3 j5wam9gi knj5qynh oo9gr5id hzawbc8m">Wednesday, June 23, 2021 at 5:30 PM</span>
			except:
				continue

			try:
				post_url = article_element.find_element(By.XPATH,'.//a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]').get_attribute('href')
				post_url = post_url.split('__cft__')[0]

				c.execute('INSERT INTO feed (post_URL, page_URL, post_time, recommended, time) \
							VALUES ("' + post_url + '","' + page_name + '","' + post_date + '","' + str(recommended) + '","' + get_date() + '")');
				conn.commit()

				log.info("\nPost: {}\nPage: {}\nPost creation date: {}\nRecommended: {}".format(post_url, page_name, post_date, recommended))

				sleep(random.randint(3,10))
			except:pass
			del action
		sleep(random.randint(6,15))

	conn.close()

def analize_video_feed():
	log.info("Analyzing Latest Video feed")
	conn = sqlite3.connect('analysisdata/suggestions.db')
	c = conn.cursor()
	driver.get('https://www.facebook.com/watch/latest')
	#sleep(10000000)

	sleep(5)
	banner = driver.find_element(By.XPATH,'//div[@role="banner"]')
	delete_element(banner)
	try:
		banner2 = driver.find_element(By.XPATH,'//div[@class="ehxjyohh be9z9djy lpgh02oy dsne8k7f"]')
		delete_element(banner2)
	except:pass
	counter = 0

	last_element = ''
	while True:
		try:
			video_elements = driver.find_elements(By.XPATH,"//div[@class='l9j0dhe7']")
			if last_element != '':
				indx = video_elements.index(last_element)
				video_elements = video_elements[indx+1:]

			if video_elements == []:
				break

			for video_element in video_elements:
				if counter == 600:
					conn.close()
					return
				last_element = video_element
				video_element.location_once_scrolled_into_view
				sleep(2)
				# Save screenshot
				data = video_element.screenshot_as_png
				with open("analysisdata/v_"+get_date()+".png",'wb') as f:
					f.write(data)

				links = video_element.find_elements(By.XPATH,".//a[@role='link']")
				#page_name = page_name.split('__cft__')[0]
				try:
					video_link = links[0].get_attribute('href')
					page_link = links[1].get_attribute('href')
					description = links[2].text


					post_date = video_element.find_element(By.XPATH,".//div[@class='aov4n071']").text

					c.execute('INSERT INTO video_feed (post_URL, page_URL, post_time, description, time) \
								VALUES ("' + video_link + '","' + page_link + '","' + post_date + '","' + description + '","' + get_date() + '")');
					conn.commit()


					log.info("\nPost: {}\nPage: {}\nDescription: {}\nPost creation date: {}".format(video_link, page_link, description, post_date))

				except Exception as e:
					print(e)
					pass
				counter += 1
				sleep(random.randint(3,10))

			sleep(random.randint(3,10))
		except:
			print("?")
	conn.close()

def analize_main_video_feed():
	log.info("Analyzing Video feed")
	conn = sqlite3.connect('analysisdata/suggestions.db')
	c = conn.cursor()
	driver.get('https://www.facebook.com/watch/')
	driver.get_screenshot_as_file("analysisdata/first_mv_"+get_date()+".png")
	sleep(3)
	driver.get('https://www.facebook.com/watch/')
	driver.get_screenshot_as_file("analysisdata/first_mv_"+get_date()+".png")
	sleep(3)
	driver.get('https://www.facebook.com/watch/')
	driver.get_screenshot_as_file("analysisdata/first_mv_"+get_date()+".png")
	sleep(3)

	sleep(5)
	banner = driver.find_element(By.XPATH,'//div[@role="banner"]')
	delete_element(banner)
	counter = 0

	last_element = ''
	while True:
		try:
			video_elements = driver.find_elements(By.XPATH,"//div[@class='j83agx80 cbu4d94t buofh1pr kvgmc6g5 tvfksri0 oygrvhab ozuftl9m ihqw7lf3']")
			if last_element != '':
				indx = video_elements.index(last_element)
				video_elements = video_elements[indx+1:]

			if video_elements == []:
				break
			follow = 0
			for video_element in video_elements:
				if counter == 300:
					conn.close()
					return
				last_element = video_element
				video_element.location_once_scrolled_into_view
				sleep(2)
				# Save screenshot
				data = video_element.screenshot_as_png
				with open("analysisdata/mv_"+get_date()+".png",'wb') as f:
					f.write(data)

				links = video_element.find_elements(By.XPATH,".//a[@role='link']")
				try:
					description = video_element.find_element(By.XPATH,'.//div[@class="n1l5q3vz"]').text
					description = description.replace("'","%")
					description = description.replace('"','%')
					#for el in links:
					#	print(el.get_attribute('href'))
					page_link = links[0].get_attribute('href')
					page_link = page_link.split('?__cft__')[0]
					page_link = page_link.replace("watch/","")

					post_link = links[2].get_attribute('href')
					post_link = post_link.split('?__cft__')[0]
					#post_link = video_element.find_element(By.XPATH,'.//div[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]')


					post_date = links[2].text


					#try:
					c.execute('INSERT INTO main_video_feed (post_URL, page_URL, post_time, description, follow, time) \
								VALUES ("' + post_link + '","' + page_link + '","' + post_date + '","' + description + '","' + str(follow) + '","' + get_date() + '")');
					conn.commit()
					#except sqlite3.IntegrityError:
					#	continue

					log.info("\nPost: {}\nPage: {}\nDescription: {}\nPost creation date: {}\nFollow suggestion: {}".format(post_link, page_link, description, post_date, str(follow)))

				except Exception as e:
					print(e)
					pass
				counter += 1
				sleep(random.randint(3,10))

			sleep(random.randint(3,10))
		except:
			print("?")
	conn.close()

def login(key):
	# Log in to Facebook
	driver.get("https://www.facebook.com")
	driver.find_element(By.XPATH,"//button[@data-cookiebanner='accept_button']").click()
	sleep(1)
	# Decrypt password
	with open(os.getcwd()+'/'+'.saved_data','r') as f:
		text = f.read()
		text = text.split('\n')
		email = aes_decrypt(text[0],key)
		encp = text[1]
	password = aes_decrypt(encp, key)
	# Input email and password, then click Log In button.
	driver.find_element(By.NAME,"email").send_keys(email)
	driver.find_element(By.NAME,"pass").send_keys(password)
	driver.find_element(By.XPATH,"//*[text() = 'Log In']").click()
	sleep(3)


def main():
	global driver
	global log

	log = logging.getLogger()
	log.setLevel(logging.INFO)
	fileformat = logging.Formatter("%(asctime)s: %(message)s",
									datefmt=DATE_FORMAT)

	file = logging.FileHandler("analysis_logs.log")
	file.setFormatter(fileformat)
	log.addHandler(file)

	console = logging.StreamHandler()
	console.setFormatter(fileformat)
	log.addHandler(console)

	'''
	profile_path = '/home/'+ os.getlogin() + '/.mozilla/firefox/'
	profile_path += [a for a in os.listdir(profile_path) if a.endswith('.default-esr')][0]
	fx_prof = webdriver.FirefoxProfile(profile_path)
	'''

	#exec_path = input("Enter geckodriver executable path:")
	#exec_path = '/home/'+ os.getlogin() + '/Downloads/geckodriver/geckodriver'
	#try:
		#os.system("rm -r 	analysisdata")
	#except: pass


	try: os.mkdir("analysisdata")
	except: pass

	profile_path = os.getcwd()+'/fx_profile'

	fx_options = Options()
	fx_options.add_argument("--profile")
	fx_options.add_argument(profile_path)
	#fx_options.add_argument("--headless")
	driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options = fx_options)


	#key = getpass.getpass(prompt='Password: ', stream=None)
	#key = Hash(key)
	#login(key)


	try:
		create_analysis_table()
		create_video_feed()
		create_main_video_feed()
	except:pass
	try:
		analize_feed()
	except: pass

	analize_video_feed()
	analize_main_video_feed()


main()
