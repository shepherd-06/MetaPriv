import sqlite3

def create_connection():
    """ Create a database connection to the SQLite database specified by db_file """
    conn = None
    db_file = "userdata.db"
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)

    return conn

def create_table(conn):
    """ Create a table from the create_table_sql statement """
    try:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                masterPassword TEXT,
                createdOn DATETIME NOT NULL,
                lastSeenOn DATETIME,
                fb_username TEXT,
                fb_password TEXT,
                is_fb_reset INTEGER
            )
        """)
    except Exception as e:
        print(e)

def new_page(pagename):
	# Add a new page to database
	conn = sqlite3.connect('userdata/likes.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE "{}"
	             ([post] text PRIMARY KEY,
	              [time] date)'''.format(pagename))
	conn.commit()
	conn.close()

def new_keyword(keyword):
	# Add a new keyword to database
	conn = sqlite3.connect('userdata/pages.db')
	c = conn.cursor()
	c.execute('INSERT INTO categories (category) \
			  		   VALUES (?)', [keyword])
	conn.commit()
	ID = c.lastrowid
	conn.close()
	return ID

def create_categ_table():
	# Create pages database to store page urls based on a keyword
	conn = sqlite3.connect('userdata/pages.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE categories
	             ([ID] INTEGER PRIMARY KEY,
	              [category] text)''')
	c.execute('''CREATE TABLE pages
	             ([PID] INTEGER PRIMARY KEY,
	              [URL] text,
	              [categID] int)''')
	conn.commit()
	conn.close()

def create_video_db(keyword):
	conn = sqlite3.connect('userdata/watched_videos.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE "{}"
	             ([post_URL] text PRIMARY KEY,
	              [page_URL] text,
	              [liked] INTEGER,
	              [time] date)'''.format(keyword))
	conn.commit()
	conn.close()

def create_clicked_links_db():
	conn = sqlite3.connect('userdata/clicked_links.db')
	c = conn.cursor()
	c.execute('''CREATE TABLE clicked_links
	             ([post_URL] text PRIMARY KEY,
	              [time] date)''')
	conn.commit()
	conn.close()
