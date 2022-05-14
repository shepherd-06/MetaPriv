import tkinter as tk
import sqlite3

from crypto import Hash, aes_encrypt, aes_decrypt

class StatsWindow(tk.Frame):

	def __init__(self, parent, key, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.mainwindow = parent

		# Window options
		self.mainwindow.title("MetaPriv Statistics")
		self.mainwindow.option_add('*tearOff', 'FALSE')
		self.mainwindow.protocol('WM_DELETE_WINDOW', self.close)

		self.mainwindow.grid_rowconfigure(0, weight=1)
		self.mainwindow.grid_rowconfigure(1, weight=1)
		self.mainwindow.grid_rowconfigure(2, weight=1)
		self.mainwindow.grid_rowconfigure(3, weight=1)
		self.mainwindow.grid_columnconfigure(0, weight=1)
		self.mainwindow.grid_columnconfigure(1, weight=1)
		self.mainwindow.grid_columnconfigure(2, weight=1)
		
		
		########### Canvas ###########
		self.canvas = tk.Canvas(self.mainwindow, width=1400, height=700, background='white')
		self.canvas.grid(row=0, column=0)

		Keywords = {}
		conn = sqlite3.connect('userdata/pages.db')
		c = conn.cursor()
		c.execute("SELECT * FROM categories")
		keywords_in_db = c.fetchall()

		for keyword in keywords_in_db:
			#tk.Label(self.mainwindow, text=aes_decrypt(keyword[1],key)).grid(row=0,column=0)
			liked_posts = 0
			liked_pages = 0
			ID, word = keyword
			c.execute('SELECT URL FROM pages WHERE categID IS '+str(ID))
			urls = c.fetchall()
			conn.close()

			conn = sqlite3.connect('userdata/likes.db')
			c = conn.cursor()
			c.execute("SELECT name FROM sqlite_master WHERE type='table';")
			liked_pages_urls = c.fetchall()
			for url in urls:
				if url in liked_pages_urls:
					c.execute('SELECT time FROM "'+url[0]+'"')
					table_length = len(c.fetchall())
					liked_posts += table_length
					liked_pages += 1

			conn.close()
			Keywords[aes_decrypt(word,key)] = (liked_posts,liked_pages)

		print(Keywords)

	def close(self):
		self.mainwindow.destroy()

'''
key = Hash('aaaaaaaa')
stats = tk.Tk()
stats.resizable(False, False)
StatsWindow(stats,key)
stats.mainloop()
'''