import tkinter as tk
from tkinter import ttk
import numpy as np 
import sqlite3
import pandas as pd
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
from pandastable import Table
from crypto import Hash, aes_decrypt


class Keyword:
	def __init__(self,key):
		self.key = key
		self.video_list = []
		self.pages = {}

	def add_videos(self,video_list):
		for vid in video_list:
			post, page, liked, _ = vid
			self.video_list.append([aes_decrypt(post,self.key),aes_decrypt(page,self.key),liked])

	def get_videos(self):
		return self.video_list

	def add_page(self,page,post_list):
		self.pages[page] = post_list

	def get_pages_dict(self):
		return self.pages


class PostsWindow:
	def __init__(self,pages_dict,name):

		def plot(choice):
			try:self.plot_frame.destroy()
			except:pass
			choice = variable.get()
			self.plot(self.pages_dict[choice])

		self.mainwindow = tk.Tk()
		title = name + ' posts liked'
		self.mainwindow.title(title)
		self.mainwindow.protocol('WM_DELETE_WINDOW', self.close)
		self.pages_dict = pages_dict
		pages = list(self.pages_dict.keys())

		variable = tk.StringVar()
		variable.set(pages[0])

		dropdown = tk.OptionMenu(self.mainwindow,variable,*pages,command=plot)
		dropdown.pack(fill='x',expand=True)
		self.plot(self.pages_dict[variable.get()])

	def plot(self,post_list):
		df = pd.DataFrame({'Post_URL': post_list })

		self.plot_frame = tk.Frame(self.mainwindow)
		self.plot_frame.pack(fill='x',expand=True)

		pt = Table(self.plot_frame,dataframe=df,width=900,maxcellwidth=900)
		pt.show()

	def close(self):
		self.mainwindow.destroy()

	def start(self):
		self.mainwindow.mainloop()


class VideoWindow:
	def __init__(self,video_list,name):
		df = pd.DataFrame(video_list, columns = ('Post_URL', 'Page_URL','Liked'))
		# Window options
		self.mainwindow = tk.Tk()
		title = name + ' videos watched'
		self.mainwindow.title(title)
		self.mainwindow.protocol('WM_DELETE_WINDOW', self.close)
		frame = tk.Frame(self.mainwindow)
		frame.pack(fill='x',expand=True)

		pt = Table(frame,dataframe=df,width=1400,maxcellwidth=700)
		pt.show()

	def close(self):
		self.mainwindow.destroy()

	def start(self):
		self.mainwindow.mainloop()

class AdsWindow:
	def __init__(self, ad_list):
		df = pd.DataFrame({'Post_URL': ad_list })
		# Window options
		self.mainwindow = tk.Tk()
		title = ' Ads clicked'
		self.mainwindow.title(title)
		self.mainwindow.protocol('WM_DELETE_WINDOW', self.close)
		frame = tk.Frame(self.mainwindow)
		frame.pack(fill='x',expand=True)

		pt = Table(frame,dataframe=df,width=1400,maxcellwidth=700)
		pt.show()

	def close(self):
		self.mainwindow.destroy()

	def start(self):
		self.mainwindow.mainloop()


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

		tabs = ttk.Notebook(self.mainwindow)
		tabs.grid(row=0,column=0,columnspan=3)

		self.keyword_list = []
		self.liked_posts_list = []
		self.liked_pages_list = []
		self.watched_videos_list = []
		self.liked_videos_list = []
		self.words = {}
		#pages = []
		conn = sqlite3.connect('userdata/pages.db')
		c = conn.cursor()
		c.execute("SELECT * FROM categories")
		keywords_in_db = c.fetchall()
		conn.close()

		for keyword in keywords_in_db:
			liked_posts = 0
			liked_pages = 0
			ID, word = keyword
			self.words[aes_decrypt(word,key)] = Keyword(key)###
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
					c.execute('SELECT post FROM "'+url[0]+'"')
					posts = c.fetchall()
					p = []
					for post in posts:
						p.append(aes_decrypt(post[0],key))
					self.words[aes_decrypt(word,key)].add_page(aes_decrypt(url[0],key),p)
					table_length = len(posts)
					liked_posts += table_length
					liked_pages += 1

			conn.close()
			n_watched_videos = 0
			watched_videos = []
			n_liked_videos = 0
			liked_videos = []
			#try:
			conn = sqlite3.connect('userdata/watched_videos.db')
			c = conn.cursor()
			c.execute('SELECT * FROM "'+word+'"')
			watched_videos = c.fetchall()
			n_watched_videos = len(watched_videos)
			c.execute('SELECT * FROM "'+word+'" WHERE liked IS 1')
			liked_videos = c.fetchall()
			n_liked_videos = len(liked_videos)
			conn.close()
			#except: pass
			self.keyword_list.append(aes_decrypt(word,key))
			self.liked_posts_list.append(liked_posts)
			self.liked_pages_list.append(liked_pages)
			self.watched_videos_list.append(n_watched_videos)
			self.liked_videos_list.append(n_liked_videos)

			# Add videos to keyword object
			self.words[aes_decrypt(word,key)].add_videos(watched_videos)

		self.ad_list = []
		try:
			conn = sqlite3.connect('userdata/clicked_links.db')
			c = conn.cursor()
			c.execute("SELECT post_URL FROM clicked_links")
			ad_posts = c.fetchall()
			for ad in ad_posts:
				self.ad_list.append(aes_decrypt(ad[0],key))
		except: pass

		self.frame1 = ttk.Frame(tabs)
		self.frame2 = ttk.Frame(tabs)
		self.frame3 = ttk.Frame(tabs)
		self.frame4 = ttk.Frame(tabs)
		tabs.add(self.frame1, text="Everything")
		tabs.add(self.frame2, text="Liked posts")
		tabs.add(self.frame3, text="Liked pages")
		tabs.add(self.frame4, text="Videos watched")

		self.frame1_plot()
		self.frame2_plot()
		self.frame3_plot()
		self.frame4_plot()

		# setting variable for Integers
		self.variable = tk.StringVar()
		self.variable.set(list(self.words.keys())[0])

		# creating widget
		dropdown = tk.OptionMenu(self.mainwindow,self.variable,*self.words)
		dropdown.grid(row=1,column=0,sticky='ew')

		watched_videos_button = tk.Button(self.mainwindow, text="Videos watched", 
			font=10, background='white',command=self.video_window)
		watched_videos_button.grid(row=1,column=1,sticky='we')#command= lambda: self.strt(key),

		posts_button = tk.Button(self.mainwindow, text="Posts liked", font=10, background='white',
			command=self.posts_window)
		posts_button.grid(row=1,column=2,sticky='we')#command= lambda: self.strt(key),

		ad_clicks_button = tk.Button(self.mainwindow, text="Ads clicked (independent of keywords)", font=10, background='white',
			command=self.ads_window)
		ad_clicks_button.grid(row=2,column=0,sticky='we',columnspan=3)


	def ads_window(self):
		window = AdsWindow(self.ad_list)
		window.start()

	def posts_window(self):
		keyword = self.variable.get()
		window = PostsWindow(self.words[keyword].get_pages_dict(),keyword)
		window.start()

	def video_window(self):
		keyword = self.variable.get()
		window = VideoWindow(self.words[keyword].get_videos(),keyword)
		window.start()

	def frame4_plot(self):
		fig = Figure(dpi=150)
		a = fig.add_subplot(111)
		a.bar(self.keyword_list,self.watched_videos_list,0.3,color='blue',label="Videos watched")

		a.set_title ("Videos watched", fontsize=16)
		a.set_ylabel("Number of (#)", fontsize=14)
		a.set_xlabel("Keywords", fontsize=14)
		a.set_ylim(bottom=0)
		a.grid(color='grey', linestyle='-', linewidth=0.5)

		self.canvas = FigureCanvasTkAgg(fig, master=self.frame4)
		self.canvas.get_tk_widget().grid(row=1,column=0,columnspan=3)
		self.canvas.draw()

		self.toolbarframe = tk.Frame(master=self.frame4)
		self.toolbarframe.grid(row=2,column=0,columnspan=3)
		toolbar = NavigationToolbar2Tk(self.canvas,self.toolbarframe)
		toolbar.update()
			
	def frame3_plot(self):
		fig = Figure(dpi=150)
		a = fig.add_subplot(111)
		a.bar(self.keyword_list,self.liked_pages_list,0.3,color='green',label="Liked pages")

		a.set_title ("Liked pages", fontsize=16)
		a.set_ylabel("Number of (#)", fontsize=14)
		a.set_xlabel("Keywords", fontsize=14)
		a.set_ylim(bottom=0)
		a.grid(color='grey', linestyle='-', linewidth=0.5)

		self.canvas = FigureCanvasTkAgg(fig, master=self.frame3)
		self.canvas.get_tk_widget().grid(row=1,column=0,columnspan=3)
		self.canvas.draw()

		self.toolbarframe = tk.Frame(master=self.frame3)
		self.toolbarframe.grid(row=2,column=0,columnspan=3)
		toolbar = NavigationToolbar2Tk(self.canvas,self.toolbarframe)
		toolbar.update()

	def frame2_plot(self):
		fig = Figure(dpi=150)
		a = fig.add_subplot(111)
		a.bar(self.keyword_list,self.liked_posts_list,0.3,color='red',label="Liked posts")

		a.set_title ("Liked posts", fontsize=16)
		a.set_ylabel("Number of (#)", fontsize=14)
		a.set_xlabel("Keywords", fontsize=14)
		a.set_ylim(bottom=0)
		a.grid(color='grey', linestyle='-', linewidth=0.5)

		self.canvas = FigureCanvasTkAgg(fig, master=self.frame2)
		self.canvas.get_tk_widget().grid(row=1,column=0,columnspan=3)
		self.canvas.draw()

		self.toolbarframe = tk.Frame(master=self.frame2)
		self.toolbarframe.grid(row=2,column=0,columnspan=3)
		toolbar = NavigationToolbar2Tk(self.canvas,self.toolbarframe)
		toolbar.update()


	def frame1_plot(self):
		X_axis = np.arange(len(self.keyword_list))

		fig = Figure(dpi=150)
		a = fig.add_subplot(111)
		text_allign_val = 0.03
		allign_val = 0.2
		bar_len = 0.3

		a.bar(X_axis-2*allign_val,self.liked_videos_list,bar_len,color='orange',label="Videos liked")
		a.bar(X_axis-allign_val,self.watched_videos_list,bar_len,color='blue',label="Videos watched")
		a.bar(X_axis,self.liked_posts_list,bar_len,color='red',label="Liked posts")
		a.bar(X_axis+allign_val,self.liked_pages_list,bar_len,color='green',label="Liked pages")

		a.legend(fontsize = 10)
		a.set_xticks(X_axis,self.keyword_list)

		a.set_title ("All Stats", fontsize=16)
		a.set_ylabel("Number of (#)", fontsize=14)
		a.set_xlabel("Keywords", fontsize=14)
		a.set_ylim(bottom=0)
		a.grid(color='grey', linestyle='-', linewidth=0.5)


		self.canvas = FigureCanvasTkAgg(fig, master=self.frame1)
		self.canvas.get_tk_widget().grid(row=1,column=0,columnspan=3)
		self.canvas.draw()

		self.toolbarframe = tk.Frame(master=self.frame1)
		self.toolbarframe.grid(row=2,column=0,columnspan=3)
		toolbar = NavigationToolbar2Tk(self.canvas,self.toolbarframe)
		toolbar.update()	

	def close(self):
		self.mainwindow.destroy()

if __name__ == '__main__':
	#password = input("Enter password: ")
	password='aaaaaaaa'
	key = Hash(password)
	stats = tk.Tk()
	stats.resizable(False, False)
	StatsWindow(stats,key)
	stats.mainloop()
