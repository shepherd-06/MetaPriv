import tkinter as tk
import numpy as np 
import sqlite3
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure

#import matplotlib.pyplot as Figure
from crypto import Hash, aes_encrypt, aes_decrypt



class StatsWindow(tk.Frame):

	def __init__(self, parent, key, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.mainwindow = parent

		# Window options
		self.mainwindow.title("MetaPriv Statistics")
		self.mainwindow.option_add('*tearOff', 'FALSE')
		self.mainwindow.protocol('WM_DELETE_WINDOW', self.close)
		'''

		self.mainwindow.grid_rowconfigure(0, weight=1)
		self.mainwindow.grid_rowconfigure(1, weight=1)
		self.mainwindow.grid_rowconfigure(2, weight=1)
		self.mainwindow.grid_rowconfigure(3, weight=1)
		self.mainwindow.grid_columnconfigure(0, weight=1)
		self.mainwindow.grid_columnconfigure(1, weight=1)
		self.mainwindow.grid_columnconfigure(2, weight=1)
		'''
		
		########### Canvas ###########
		#self.canvas = tk.Canvas(self.mainwindow, width=1400, height=700, background='white')
		#self.canvas.pack()#.grid(row=0, column=0)

		self.keyword_list = []
		self.liked_posts_list = []
		self.liked_pages_list = []
		self.watched_videos_list = []
		conn = sqlite3.connect('userdata/pages.db')
		c = conn.cursor()
		c.execute("SELECT * FROM categories")
		keywords_in_db = c.fetchall()
		conn.close()

		for keyword in keywords_in_db:
			#tk.Label(self.mainwindow, text=aes_decrypt(keyword[1],key)).grid(row=0,column=0)
			liked_posts = 0
			liked_pages = 0
			ID, word = keyword
			conn = sqlite3.connect('userdata/pages.db')
			c = conn.cursor()
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
			watched_videos = 0
			try:
				conn = sqlite3.connect('userdata/watched_videos.db')
				c = conn.cursor()
				c.execute('SELECT time FROM "'+word+'"')
				watched_videos = len(c.fetchall())
				conn.close()
			except: pass

			#Keywords[aes_decrypt(word,key)] = [liked_posts,liked_pages,watched_videos]
			self.keyword_list.append(aes_decrypt(word,key))
			self.liked_posts_list.append(liked_posts)
			self.liked_pages_list.append(liked_pages)
			self.watched_videos_list.append(watched_videos)
			

	def plot_all(self):
		X_axis = np.arange(len(self.keyword_list))

		fig = Figure(dpi=150)
		a = fig.add_subplot(111)
		text_allign_val = 0.03
		allign_val = 0.2
		bar_len = 0.3
		a.bar(X_axis-allign_val,self.watched_videos_list,bar_len,color='blue',label="Watched videos")
		'''
		for i in range(len(self.keyword_list)):
			txt = str(self.watched_videos_list[i])
			a.text(X_axis[i]-allign_val-text_allign_val,self.watched_videos_list[i]+1,txt,color='blue',fontsize = 5)
		'''
		a.bar(X_axis,self.liked_posts_list,bar_len,color='red',label="Liked posts")
		'''
		for i in range(len(self.keyword_list)):
			txt = str(self.liked_posts_list[i])
			a.text(X_axis[i]-text_allign_val,self.liked_posts_list[i]+1,txt,color='red',fontsize = 5)
		'''
		a.bar(X_axis+allign_val,self.liked_pages_list,bar_len,color='green',label="Liked pages")
		'''
		for i in range(len(self.keyword_list)):
			txt = str(self.liked_pages_list[i]) 
			a.text(X_axis[i]+allign_val-text_allign_val,self.liked_pages_list[i]+1,txt,color='green',fontsize = 5)
		'''

		a.legend(fontsize = 10)
		a.set_xticks(X_axis,self.keyword_list)
		#print(X_axis)

		#a.set_title ("Estimation Grid", fontsize=16)
		a.set_ylabel("Number of (#)", fontsize=14)
		a.set_xlabel("Keywords", fontsize=14)
		a.set_ylim(bottom=0)
		#fig.subplots_adjust(top=0.97,bottom=0.15,left=0.120,right=0.99,hspace=1,wspace=0.2)
		#fig.ylim(bottom=0)

		canvas = FigureCanvasTkAgg(fig, master=self.mainwindow)
		canvas.get_tk_widget().pack()
		toolbar = NavigationToolbar2Tk(canvas,self.mainwindow)
		toolbar.update()
		canvas.draw()

	def close(self):
		self.mainwindow.destroy()

if __name__ == "__main__":
	key = Hash('qwerty123')
	stats = tk.Tk()
	stats.resizable(False, False)
	StatsWindow(stats,key)
	stats.mainloop()

#main()