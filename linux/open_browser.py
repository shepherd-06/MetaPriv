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
import os

profile_exists = os.path.isdir(os.getcwd()+'/fx_profile')
if not profile_exists:
	tempdirs = os.listdir(gettempdir())
# webdriver options
fx_options = Options()
profile_path = os.getcwd()+'/fx_profile'
if profile_exists:
	fx_options.add_argument("--profile")
	fx_options.add_argument(profile_path)
# Start
driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()),options = fx_options)
driver.set_window_size(1400,800)
driver.get('https://www.facebook.com/')