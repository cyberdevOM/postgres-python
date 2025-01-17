import bcrypt
from database import Database

class UserAccounts: # this class is used to manage user accounts
    def __init__(self, db): # this is the constructor for the UserAccounts class
        self.db = Database(dbname='wargame', user='postgres', password='post', host='localhost')


    def input_sanitiser(self, input_str): # this function is required for security and input snaitisation.
        return input_str.strip().replace(";$^£&*()+-=[]{}|:<>,./", "")

    def get_user_info(self, email):
        try: # try and get user info from the database using the email.
            self.db.cur.execute("SELECT id, username, email FROM players WHERE email = %s", (email,))
            user_info = self.db.cur.fetchone()
            return user_info
        except Exception as e:
            print(f"Error fetching user info: {e}")
            return None

    def get_password_hash(self, player_id):
        try: # fetch the password hash from the database using the player_id, used for hash comparison and login
            self.db.cur.execute("SELECT password_hash FROM passwords WHERE player_id = %s", (player_id,))
            password_hash = self.db.cur.fetchone()
            return password_hash[0] if password_hash else None # [0] referse to the first element in the tuple
        except Exception as e:
            print(f"Error fetching password hash: {e}")
            return None

    # login function takes user input and passes it to the .get_user_info() and .get_password_hash() functions
    # if the user is found and the password hash is correct, the user is logged in
    def login(self, user_number): 
        print(f'Login user:{user_number}')
        email = input("Enter your email: ").strip().replace(";$^£&*()+-=[]{}|:<>,./", "")
        password = input("Enter your password: ").strip().replace(";$^£&*()+-=[]{}|:<>,./", "")
        user_info = self.get_user_info(email)
        if user_info:
            player_id, username, email = user_info
            if self.db.is_user_logged_in(player_id):
                print("User already logged in \n")
                return None
            get_password_hash = self.get_password_hash(player_id) # player password hash
            
            if get_password_hash and bcrypt.checkpw(password.encode('utf-8'), get_password_hash.encode('utf-8')):
                # if the password hash and a password hash entered by the user match, the user is logged in.
                print(f'login user {user_number} successful \n')
                self.db.add_logged_in_user(player_id) # add the user to the logged in users table, this avoids the same user being logged in twice
                return player_id, username, email
            else:
                print(f'login {user_number} failed')
                return None
        else:
            print("User not found")
            return None # if the user is not found, return None
        
    # register function takes user input and creates a new user in the database
    # to improve on this id create a function to check if the user already exists, if this is the case, return an error.
    def register(self, username, email, password): 
        print("Register")
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        try:
            player_id = self.db.generate_uid()
            self.db.cur.execute("INSERT INTO players (id, username, email) VALUES (%s, %s, %s)", (player_id, username, email))
            self.db.cur.execute("INSERT INTO passwords (player_id, password_hash) VALUES (%s, %s)", (player_id, password_hash))
            self.db.conn.commit() # commit the changes to the database (save)
            return True # return true to indicate that the user has been created successfully
        except Exception as e:
            print(f"Error registering user: {e}")
            self.db.conn.rollback()
            return False
        
    def logout(self, player1_id, player2_id):
        try: # remove the user1 and 2 specified from the logged in users table
            self.db.remove_logged_in_user(player1_id)
        except Exception: # if there is an error, pass. this is a type of force remove.
            pass 
        
        try:
            self.db.remove_logged_in_user(player2_id)
        except Exception:
            pass
        
        exit(0) # exit the program
    def UAclose(self): # close the cursor and connection to the database
        self.db.cur.close()
        self.db.conn.close()

class userStatistics: # this class is used to get the user stats from the database
    def __init__(self, db): # this is the constructor for the UserAccounts class
        self.db = Database(dbname='wargame', user='postgres', password='post', host='localhost')

    def get_user_stats(self, player_id): # get the user stats from the database using the player_id 
        try: 
            self.db.cur.execute("SELECT username, rounds_won, games_won, games_lost FROM players WHERE player_id = %s", (player_id,))
            stats = self.db.cur.fetchone()
            return stats
        except Exception as e:
            print(f"Error fetching user stats: {e}")
            return None
    
    def get_recent_game_ids(self, player_id): # get the recent game ids from the database using the player_id
        try:
            self.db.cur.execute("SELECT id FROM games WHERE player_id = %s AND date >= NOW() - INTERVAL '5 days'", (player_id,))
            recent_games = self.db.cur.fetchall()
            return recent_games
        except Exception as e:
            print(f"Error fetching recent games: {e}")
            return None
    
    def game_indiviual_stats(self, player_id, game_id): # get the individual game stats from the database using the player_id and game_id
        try:
            self.db.cur.execute("SELECT rounds_won, rounds_lost FROM game_rounds WHERE player_id = %s AND game_id = %s", (player_id, game_id))
            game_stats = self.db.cur.fetchone()
            self.db.cur.execute("SELECT winner_id FROM games WHERE id = %s", (game_id,))
            winner_id = self.db.cur.fetchone()
            return game_stats, winner_id
        except Exception as e: # if there is an error, print the error and return None
            print(f"Error fetching game stats: {e}")
            return None

    def USclose(self): # close the cursor and connection to the database
        self.db.cur.close()
        self.db.conn.close()