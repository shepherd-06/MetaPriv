import os
from metapriv.crypto import aes_encrypt
from datetime import datetime
import random
from time import sleep as Sleep
import multiprocessing as mp


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

## ##########################################
## This file might need further clean up. 
## TODO: add logs.
## ##########################################


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


def sleep(seconds):
    #, watching_video = False):
    time = 0
    net_up = 1
    while True:
        # Computation time. On average the waiting time == seconds parameter
        if CHECK_NET.value:
            response = os.system("ping -c 1 -w2 " + "www.google.com" + " > /dev/null 2>&1")
            if response != 0:
                if net_up:
                    print(get_date()+": "+"No internet.")
                    Sleep(1)
                    net_up = 0
        net_up = 1
        Sleep(1-0.003)
        time += 1
        if BREAK_SLEEP.value:
            break
        if STOP_WATCHING.value:
            break
        if time == seconds:
            break
