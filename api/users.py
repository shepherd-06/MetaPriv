from uuid import uuid4
from datetime import datetime
from metapriv.database_management import create_connection
import bcrypt

def create_user(username, password):
    conn = create_connection()
    if conn is None:
        print("Conn is None")
        return None
    try:
        """ Create a new user into the users table """
        sql = ''' INSERT INTO users(id, username, password, masterPassword, createdOn, lastSeenOn)
                VALUES(?,?,?,?,?,?) '''
        id = str(uuid4())  # Generate a unique user ID
        created_on = datetime.now()  # Current time for createdOn and lastSeenOn
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_data = (id, username, hashed_password, None, created_on, created_on)
        
        cur = conn.cursor()
        cur.execute(sql, user_data)
        conn.commit()
        return cur.lastrowid  # Return the ID of the created user
    finally:
        conn.close()


def get_user_by_username(username):
    """ Query user by username """
    conn = create_connection()
    if conn is None:
        print("Cannot connect to the database.")
        return None
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username=?", (username,))
        rows = cur.fetchall()
        
        for row in rows:
            print(row)  # or return row based on your application's requirements

        return rows  # Return the fetched data
    finally:
        conn.close()

def login_user(username, password):
    conn = create_connection()
    if conn is None:
        print("Cannot connect to the database.")
        return None

    """ Check user credentials """
    sql = 'SELECT password FROM users WHERE username=?'
    cur = conn.cursor()
    
    try:
        cur.execute(sql, (username,))
        row = cur.fetchone()
        if row is None:
            print("User not found.")
            return None
        stored_password = row[0]

        # Compare the stored password with the one provided
        if bcrypt.checkpw(password.encode('utf-8'), stored_password):
            print("Login successful!")
            user = get_user_by_username(username)
            return user
        else:
            print("Password is incorrect.")
            return None
    except Exception as e:
        print("An error occurred:", e)
        return None
    finally:
        conn.close()
        

def set_or_verify_master_password(user_id, master_password):
    # Logic to set or verify the master password
    # This should interact with your database
    # Return True if successful, False otherwise
    conn = create_connection()
    if conn is None:
        print("Cannot connect to the database.")
        return None
    
    try:
        cur = conn.cursor()
        cur.execute("SELECT masterPassword FROM users WHERE id=?", (user_id,))
        row = cur.fetchone()
        
        if row:
            # check if the password match, is master-password exist.
            # set new password if masterpassword field is none.
            stored_master_password = row[0]
            if stored_master_password:
                # Verify the existing master password
                if bcrypt.checkpw(master_password.encode('utf-8'), stored_master_password):
                    print("Master password verified successfully.")
                    return True
                else:
                    print("Incorrect master password.")
                    return False
            else:
                # Set the master password if it hasn't been set
                hashed_password = bcrypt.hashpw(master_password.encode('utf-8'), bcrypt.gensalt())
                cur.execute("UPDATE users SET masterPassword=? WHERE id=?", (hashed_password, user_id))
                conn.commit()
                print("Master password set successfully.")
                return True
        else:
            print("No User found with given ID")
            return False
    finally:
        conn.close()