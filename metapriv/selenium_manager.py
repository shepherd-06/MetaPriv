import threading
import sqlite3
from time import sleep
from metapriv.crypto import aes_encrypt, aes_decrypt
from selenium.webdriver.common.by import By
from random import random
from metapriv.utilities import *
from datetime import timedelta
from selenium.common.exceptions import NoSuchElementException
from metapriv.database_management import *
from selenium.webdriver import ActionChains


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