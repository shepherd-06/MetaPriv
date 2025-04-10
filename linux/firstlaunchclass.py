import os
import sys
import tkinter as tk
from base64 import b64encode
# imports from created files 
from metapriv.crypto import Hash, aes_encrypt
from passwordclass import Create_Password_UI
from datetime import datetime


INFO_TEXT = """Welcome to MetaPriv!
This is your first run, so please input your
facebook credentials and a seed keyword. 
This is a one time input, as new keywords 
will be generated automatically and the 
login will happen from a browser profile 
folder after the first run.\n"""

def get_date():
	# Get formatted date for logs
	now = datetime.now()
	formatted_date = now.strftime('%Y-%m-%d %H:%M:%S')
	return formatted_date

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
		# Create encrypted file used by the BOT
		with open(os.getcwd()+'/'+'.saved_data','w') as f:
			f.write(aes_encrypt(self.Email.get(),self.h_password)+'\n')
			f.write(aes_encrypt(self.Password.get(),self.h_password)+'\n')
			enc_keyword = aes_encrypt(self.Keyword.get().split(' ')[0]+'|0',self.h_password)
			f.write(enc_keyword + '\n')
			f.write(b64encode(os.urandom(16)).decode('utf-8')+'\n')
			f.write(self.salt+'\n')
			f.write(b64encode(self.h_salted_password).decode('utf-8')+'\n')
			timestmap = get_date()
			f.write(b64encode(Hash(b64encode(self.h_password).decode('utf-8') + timestmap + enc_keyword)).decode('utf-8')+'\n')
			f.write(timestmap)

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
