import os
import sys
import tkinter as tk
from base64 import b64encode
# imports from created files 
from crypto import Hash, aes_encrypt
from passwordclass import Create_Password_UI


INFO_TEXT = """Welcome to MetaPriv!
This is your first run, so please input your
facebook credentials, a seed keyword and the 
browser you mostly use (Firefox or Chrome). 
This is a one time input, as new keywords 
will be generated automatically and the 
login will happen from a browser profile 
folder after the first run.\n"""

class First_launch_UI:
	def __init__(self):
		# Create password UI
		self.choose_password()
		# Window options
		self.mainwindow = tk.Tk()
		self.mainwindow.title("Choose options")
		self.mainwindow.resizable(False, False)
		self.mainwindow.protocol('WM_DELETE_WINDOW', self.close)

		# Info label
		tk.Label(self.mainwindow, text=INFO_TEXT).grid(row=0, column=0,columnspan=2)

		# Facebook credentials
		tk.Label(self.mainwindow, text="Facebook Credentials:").grid(row=1, column=0,columnspan=2)
		tk.Label(self.mainwindow, text="Email: ").grid(row=2, column=0)
		self.Email = tk.Entry(self.mainwindow)
		self.Email.grid(row=2, column=1)

		tk.Label(self.mainwindow, text="Password: ").grid(row=3, column=0)
		self.Password = tk.Entry(self.mainwindow,show='*')
		self.Password.grid(row=3, column=1)

		self.hidden = True
		self.check_box = tk.Checkbutton(self.mainwindow, text='Show password', command=self.showpass).grid(row=4, columnspan=2)

		# Keyword imput
		tk.Label(self.mainwindow, text="keyword: ").grid(row=5, column=0)
		self.Keyword = tk.Entry(self.mainwindow)
		self.Keyword.grid(row=5, column=1)

		# Browser choice
		self.browser = tk.StringVar()
		R1 = tk.Radiobutton(self.mainwindow, text="Chrome", variable=self.browser, value='Chrome').grid(row=6, column=0)
		R2 = tk.Radiobutton(self.mainwindow, text="Firefox", variable=self.browser, value='Firefox').grid(row=6, column=1)

		# Invalid input comment
		self.comment = tk.Label(self.mainwindow, text="")
		self.comment.grid(row=7, column=0)

		# Continue button
		self.continue_button = tk.Button(self.mainwindow, text="Continue", 
			command=self.continue_to_next_window).grid(row=7, column=1)

	def showpass(self):
		# Show/hide password
		if self.hidden:
			self.Password.configure(show='')
			self.hidden = False
		else:
			self.Password.configure(show='*')
			self.hidden = True

	def continue_to_next_window(self):
		if self.Email.get() == '':
			self.comment.configure(text="Input Email.")
			return
		if self.Password.get() == '':
			self.comment.configure(text="Input Password.")
			return
		if self.Keyword.get() == '':
			self.comment.configure(text="Input Keyword.")
			return
		if self.browser.get() == '':
			self.comment.configure(text="Choose Browser.")
			return
		# Create encrypted file used by the BOT
		with open(os.getcwd()+'\\'+'.saved_data','w') as f:
			f.write(aes_encrypt(self.Email.get(),self.h_password)+'\n')
			f.write(aes_encrypt(self.Password.get(),self.h_password)+'\n')
			enc_keyword = aes_encrypt(self.Keyword.get()+'|0',self.h_password)
			f.write(enc_keyword + '\n')
			f.write(aes_encrypt(self.browser.get(),self.h_password)+'\n')
			f.write(self.salt+'\n')
			f.write(b64encode(self.h_salted_password).decode('utf-8')+'\n')
			f.write(b64encode(Hash(self.salt + enc_keyword)).decode('utf-8'))
		self.mainwindow.destroy()

	def start(self):
		self.mainwindow.mainloop()

	def close(self):
		sys.exit()

	def choose_password(self):
		passwrd_class = Create_Password_UI(None)
		# Window options
		passwrd_class.title("Choose password")
		passwrd_class.resizable(False, False)
		passwrd_class.mainloop()
		# Encrypt salted password
		self.salt = b64encode(os.urandom(32)).decode('utf-8')
		self.h_password = Hash(passwrd_class.password)
		self.h_salted_password = Hash(self.salt + passwrd_class.password)
		passwrd_class.stop()
		del passwrd_class
