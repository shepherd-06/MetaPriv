from crypto import Hash, aes_decrypt
import os
import sqlite3

password = input("Enter your password: ")
key = Hash(password)

try: os.mkdir('decrypted_files')
except: pass

### Logs ###
with open(os.getcwd()+'/'+"bot_logs.log",'r') as f:
	text = f.read()

text = text.split('\n')
dec_text = []
for line in text:
	dec_text.append(aes_decrypt(line,key))

with open(os.getcwd()+'/'+"decrypted_files/decrypted_bot_logs.log",'w') as f:
	for line in dec_text:
		f.write(line+'\n')

### Saved Data ###
s_data = []
with open(os.getcwd()+'/'+'.saved_data','r') as f:
	text = f.read()
	text = text.split('\n')
	s_data.append(aes_decrypt(text[0],key))
	s_data.append(aes_decrypt(text[2],key))
	s_data.append(aes_decrypt(text[3],key))

with open(os.getcwd()+'/'+'decrypted_files/decrypted_saved_data','w') as f:
	f.write("Email: "+s_data[0]+'\n')
	f.write("Keyword|Usage Number: "+s_data[1]+'\n')
	f.write("Browser: "+s_data[2])

### likes.db ###
conn = sqlite3.connect('userdata/likes.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
liked_pages_urls = c.fetchall()

conn_2 = sqlite3.connect('decrypted_files/likes.db')
c2 = conn_2.cursor()

for ((url,)) in liked_pages_urls:
	dec_url = aes_decrypt(url,key)
	c2.execute('''CREATE TABLE "{}"
	             ([post] text PRIMARY KEY,
	              [time] date)'''.format(dec_url))
	conn_2.commit()

	c.execute("SELECT * FROM '" + url + "'")
	posts_time = c.fetchall()
	posts = []
	for i in posts_time:
		posts.append((aes_decrypt(i[0],key),i[1]))

	c2.executemany('INSERT INTO "' + dec_url + '" (post, time) \
				  		   VALUES (?, ?)', posts);
	conn_2.commit()

conn_2.close()
conn.commit()
conn.close()

### pages.db ###
conn = sqlite3.connect('userdata/pages.db')
c = conn.cursor()

conn_2 = sqlite3.connect('decrypted_files/pages.db')
c2 = conn_2.cursor()

c2.execute('''CREATE TABLE categories
	             ([ID] INTEGER PRIMARY KEY,
	              [category] text)''')
c2.execute('''CREATE TABLE pages
	             ([PID] INTEGER PRIMARY KEY,
	              [URL] text,
	              [categID] int)''')
conn_2.commit()

c.execute("SELECT * FROM categories")
keywords = c.fetchall()
for i in range(len(keywords)):
	keywords[i] = (keywords[i][0],aes_decrypt(keywords[i][1],key))
c2.executemany('INSERT INTO categories (ID, category) \
				  		   VALUES (?, ?)', keywords);
conn_2.commit()

c.execute("SELECT * FROM pages")
urls = c.fetchall()
for i in range(len(urls)):
	urls[i] = (urls[i][0],aes_decrypt(urls[i][1],key),urls[i][2])
c2.executemany('INSERT INTO pages (PID, URL, categID) \
				  		   VALUES (?, ?, ?)', urls);
conn_2.commit()

conn_2.close()
conn.commit()
conn.close()
###  watched_videos.db ###
conn = sqlite3.connect('userdata/watched_videos.db')
c = conn.cursor()
c.execute("SELECT name FROM sqlite_master WHERE type='table';")
words = c.fetchall()

conn_2 = sqlite3.connect('decrypted_files/watched_videos.db')
c2 = conn_2.cursor()

for ((word,)) in words:
	dec_word = aes_decrypt(word,key)
	c2.execute('''CREATE TABLE "{}"
	             ([post_URL] text PRIMARY KEY,
	              [page_URL] text,
	              [time] date)'''.format(dec_word))
	conn_2.commit()

	c.execute("SELECT * FROM '" + word + "'")
	posts_page_time = c.fetchall()
	#print(posts_page_time)

	posts = []
	for i in posts_page_time:
		posts.append( (aes_decrypt(i[0],key), aes_decrypt(i[1],key), i[2]) )
	print(posts)
	c2.executemany('INSERT INTO "' + dec_word + '" (post_URL, page_URL, time) \
				  		   VALUES (?, ?, ?)', posts);
	conn_2.commit()

conn_2.close()
conn.commit()
conn.close()



###  clicked_links.db ###
conn = sqlite3.connect('userdata/clicked_links.db')
c = conn.cursor()
c.execute("SELECT * FROM clicked_links")
posts_page_time = c.fetchall()
print(posts_page_time)
conn_2 = sqlite3.connect('decrypted_files/clicked_links.db')
c2 = conn_2.cursor()
c2.execute('''CREATE TABLE clicked_links
	             ([post_URL] text PRIMARY KEY,
	              [time] date)''')
conn_2.commit()

posts = []
for i in posts_page_time:
	posts.append( (aes_decrypt(i[0],key), i[1]) )
print(posts)

c2.executemany('INSERT INTO clicked_links (post_URL, time) \
						VALUES (?, ?)', posts);
conn_2.commit()

conn_2.close()
conn.commit()
conn.close()