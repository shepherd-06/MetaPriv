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



def analize_feed():
	log.info("Analyzing feed")

	driver.get('https://www.facebook.com')

	sleep(5)
	banner = driver.find_element(By.XPATH,'//div[@role="banner"]')
	delete_element(banner)
	counter = 0
	last_element = ''
	while True:
		article_elements = driver.find_elements(By.XPATH,"//div[@class='x1lliihq']")
		if last_element != '':
			indx = article_elements.index(last_element)
			article_elements = article_elements[indx+1:]

		if article_elements == []:
			break

		for article_element in article_elements:
			if counter == 300:
				return
			
			last_element = article_element
			article_element.location_once_scrolled_into_view
			sleep(2)
			# Save screenshot
			data = article_element.screenshot_as_png
			with open("analysisdata/f_"+get_date()+".png",'wb') as f:
				f.write(data)
			counter += 1
			print(counter)
			sleep(5)

		sleep(5)



def analize_video_feed():
	log.info("Analyzing Latest Video feed")

	driver.get('https://www.facebook.com/watch/latest')

	sleep(5)
	banner = driver.find_element(By.XPATH,'//div[@role="banner"]')
	delete_element(banner)

	counter = 0

	last_element = ''
	while True:
		video_elements = driver.find_elements(By.XPATH,"//div[@class='x1jx94hy xhk9q7s x1otrzb0 x1i1ezom x1o6z2jb xw7yly9 x1yztbdb x1dtb55y x1l90r2v x1swvt13 x1pi30zi xyamay9']")
		if last_element != '':
			indx = video_elements.index(last_element)
			video_elements = video_elements[indx+1:]

		if video_elements == []:
			break

		for video_element in video_elements:
			if counter == 300:
				return
			last_element = video_element
			video_element.location_once_scrolled_into_view
			sleep(2)
			# Save screenshot
			data = video_element.screenshot_as_png
			with open("analysisdata/v_"+get_date()+".png",'wb') as f:
				f.write(data)

			counter += 1
			sleep(5)
			print(counter)


		sleep(5)



def analize_main_video_feed():
	log.info("Analyzing Video feed")

	driver.get('https://www.facebook.com/watch/')
	sleep(3)
	driver.get('https://www.facebook.com/watch/')
	sleep(3)
	driver.get('https://www.facebook.com/watch/')
	sleep(3)

	sleep(5)
	banner = driver.find_element(By.XPATH,'//div[@role="banner"]')
	delete_element(banner)
	counter = 0

	last_element = ''
	while True:
		video_elements = driver.find_elements(By.XPATH,"//div[@class='x78zum5 xdt5ytf']")
		if last_element != '':
			indx = video_elements.index(last_element)
			video_elements = video_elements[indx+1:]

		if video_elements == []:
			break

		for video_element in video_elements[:-1]:
			if counter == 300:
				return
			last_element = video_element
			video_element.location_once_scrolled_into_view
			sleep(2)
			# Save screenshot
			data = video_element.screenshot_as_png
			with open("analysisdata/mv_"+get_date()+".png",'wb') as f:
				f.write(data)

			counter += 1
			sleep(5)
			print(counter)

		sleep(5)

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


	try: os.mkdir("analysisdata")
	except: pass

	profile_path = os.getcwd()+'/fx_profile'

	fx_options = Options()
	fx_options.add_argument("--profile")
	fx_options.add_argument(profile_path)
	driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options = fx_options)

	analize_feed()
	analize_video_feed()
	analize_main_video_feed()


main()
