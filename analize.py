# partial imports
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from time import sleep
from datetime import datetime, timedelta
# full imports
import os
import sqlite3
import random
import logging


DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
ONE_HOUR = 3600

def delete_element(element):
	driver.execute_script("""var element = arguments[0];
							element.parentNode.removeChild(element);
							""", element)

def get_date():
	now = datetime.now()
	formatted_date = now.strftime(DATE_FORMAT)
	return formatted_date

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
	c.execute('''CREATE TABLE suggested_pages
					([post_URL] text PRIMARY KEY)''')
	conn.commit()
	conn.close()

def analize_feed():
	log.info("Analyzing feed")
	conn = sqlite3.connect('analysisdata/suggestions.db')
	c = conn.cursor()
	driver.get('https://www.facebook.com')

	sleep(5)
	banner = driver.find_element_by_xpath('//div[@role="banner"]')
	delete_element(banner)

	last_element = ''
	while True:
		article_elements = driver.find_elements_by_xpath("//div[@class='lzcic4wl']")
		if last_element != '':
			indx = article_elements.index(last_element)
			article_elements = article_elements[indx+1:]

		if article_elements == []:
			break

		for article_element in article_elements:
			recommended = 0
			last_element = article_element
			article_element.location_once_scrolled_into_view
			sleep(2)

			page_name = article_element.find_element_by_xpath(".//a[@role='link']").get_attribute('href')
			page_name = page_name.split('__cft__')[0]

			try:
				suggestion_elements = article_element.find_elements_by_xpath(".//div[@aria-label='Suggested for You']//a[@role='link']")
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
				recomended_text = article_element.find_element_by_xpath('.//span [contains( text(), "Recommended Post")]')
				recommended = 1
			except Exception as e:
                                pass

			try:
				link_element = article_element.find_element_by_xpath('.//span[@class="tojvnm2t a6sixzi8 abs2jz4q a8s20v7p t1p8iaqh k5wvi7nf q3lfd5jv pk4s997a bipmatt0 cebpdrjk qowsmv63 owwhemhu dp1hu0rb dhp61c6y iyyx5f41"]//a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]')
			except NoSuchElementException:
				continue

			action = ActionChains(driver)
			try: action.move_to_element(link_element).perform()
			except: pass

			sleep(3)
			try:
				post_date = driver.find_element_by_xpath('//div[@class="__fb-light-mode"]//*').text
				#<span class="d2edcug0 hpfvmrgz qv66sw1b c1et5uql b0tq1wua e9vueds3 j5wam9gi knj5qynh oo9gr5id hzawbc8m">Wednesday, June 23, 2021 at 5:30 PM</span>
			except:
				continue
			action.move_by_offset(500, 0).perform()
			sleep(2)

			post_url = article_element.find_element_by_xpath('.//a[@class="oajrlxb2 g5ia77u1 qu0x051f esr5mh6w e9989ue4 r7d6kgcz rq0escxv nhd2j8a9 nc684nl6 p7hjln8o kvgmc6g5 cxmmr5t8 oygrvhab hcukyx3x jb3vyjys rz4wbd8a qt6c0cv9 a8nywdso i1ao9s8h esuyzwwr f1sip0of lzcic4wl gmql0nx0 gpro0wi8 b1v8xokw"]').get_attribute('href')
			post_url = post_url.split('__cft__')[0]

			try:
				c.execute('INSERT INTO feed (post_URL, page_URL, post_time, recommended, time) \
							VALUES ("' + post_url + '","' + page_name + '","' + post_date + '","' + str(recommended) + '","' + get_date() + '")');
				conn.commit()
			except sqlite3.IntegrityError:
				print("asd")
				continue

			# Save screenshot
			data = article_element.screenshot_as_png
			with open("analysisdata/"+get_date()+".png",'wb') as f:
				f.write(data)

			log.info("\nPost: {}\nPage: {}\nPost creation date: {}\nRecommended: {}".format(post_url, page_name, post_date, recommended))

			sleep(random.randint(3,10))
			del action
			#a=input("pause")
		'''
		take_break = random.randint(1,10)
		if take_break == 1:
			random_time = random.randint(10,ONE_HOUR)
			log.info("Taking a break for {} seconds".format(random_time))
			sleep(random_time)
		'''
		sleep(random.randint(3,10))

	conn.close()


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

	profile_path = '/home/'+ os.getlogin() + '/.mozilla/firefox/' 
	profile_path += [a for a in os.listdir(profile_path) if a.endswith('.default-esr')][0]
	fx_prof = webdriver.FirefoxProfile(profile_path)

	#exec_path = input("Enter geckodriver executable path:")
	exec_path = '/home/'+ os.getlogin() + '/Downloads/geckodriver/geckodriver'

	try: os.mkdir("analysisdata")
	except: pass
	driver = webdriver.Firefox(executable_path = exec_path,firefox_profile = fx_prof)

	if not os.path.isfile('analysisdata/suggestions.db'):
		create_analysis_table()

	analize_feed()

main()
