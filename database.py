import psycopg2 as psycopg2
import uuid
import bcrypt


class Database:
    def __init__(self, dbname, user, password, host):
        self.conn = psycopg2.connect(
            dbname=dbname, user=user, password=password, host=host
        ) # this creates a connection to the database, using the creds passed in.
        self.cur = self.conn.cursor() # cursor object is used to interact with the database

    def generate_uid(self): # this function generates a unique id for various uses in the database
        return uuid.uuid4().hex[:16] # random 16 char string using hex

    def get_player_name(self, player_id): # select the username from the players table where the id matches the player_id
        try:
            self.cur.execute("SELECT username FROM players WHERE id = %s", (player_id,))
            return self.cur.fetchone()[0]
        except Exception as e: # if there is an error, print the error and return None
            print(f"Error fetching player name: {e}")
            return None

    def create_game(self, player1_id, player2_id): # insert a new game into the games table with the player1_id and player2_id
        game_id = self.generate_uid()
        try:
            self.cur.execute(
                "INSERT INTO games (id, player1_id, player2_id) VALUES (%s, %s, %s)",
                (game_id, player1_id, player2_id),
            )
            self.conn.commit() 
            self.cur.execute("SELECT id FROM games WHERE id = %s", (game_id,))
            new_game_id = self.cur.fetchone() # get the id of the new game
            
            if new_game_id is None: # if there is no game id returned, raise an exception
                raise Exception("No game ID returned")
            return new_game_id
        except Exception as e: # if there is an error, print the error and rollback the transaction
            print(f"Error inserting game: {e}")
            self.conn.rollback()
            raise

    def create_game_round(self, game_id, player_id): # insert a new game round into the game_rounds table with the game_id and player_id
        try:
            query = "INSERT INTO game_rounds (game_id, player_id) VALUES (%s, %s) RETURNING id"
            self.cur.execute(query, (game_id, player_id))
            self.conn.commit()
            
            return self.cur.fetchone()[0]
        except Exception as e: 
            print(f"Error inserting game round: {e}")
            self.conn.rollback()
            raise

    def update_round_stats(self, game_id, player_id, column):
        try:
            query = f"UPDATE game_rounds SET {column} = {column} + 1 WHERE game_id = %s AND player_id = %s"
            self.cur.execute(query, (game_id, player_id))
            self.conn.commit()
            # print(f"Round stats updated for game {game_id} and player {player_id}")
        except Exception as e:
            print(f"Error updating round stats: {e}")
            self.conn.rollback()
            raise

    def update_player_stats(self, player_id, column): # update the player stats for the player_id and column
        try:
            query = f"UPDATE players SET {column} = {column} + 1 WHERE id = %s"
            self.cur.execute(query, (player_id,))
            self.conn.commit()

        except Exception as e:
            print(f"Error updating player stats: {e}")
            self.conn.rollback()
            raise

    def get_game_rounds(self, game_id):
        self.cur.execute(
            "SELECT player_id, rounds_won FROM game_rounds WHERE game_id = %s", (game_id,)
        )
        return self.cur.fetchall()
    
    def update_player_at_game_end(self, player_id, column, value):
        try: # update the player stats for the player_id and column
            query = f"UPDATE players SET {column} = {column} + {value} WHERE id = %s"
            self.cur.execute(query, (player_id,))
            self.conn.commit()

        except Exception as e:
            print(f"Error updating player stats: {e}")
            self.conn.rollback()
            raise

    def record_game(self, game_id, winner_id):
        self.cur.execute(
            "UPDATE games SET winner_id = %s WHERE id = %s", (winner_id, game_id)
        )
        self.conn.commit()

    def add_logged_in_user(self, player_id): # insert the player_id into the logged_in_users table
        self.cur.execute("INSERT INTO logged_in_users (user_id) VALUES (%s)", (player_id,))
        self.conn.commit()
    
    def is_user_logged_in(self, player_id):
        try: # check if the player_id is in the logged_in_users table
            self.cur.execute("SELECT COUNT(*) FROM logged_in_users WHERE user_id = %s", (player_id,))
            result = self.cur.fetchone()
            if result and int(result[0]) > 0:
                return True
            return False
        except Exception as e: # if there is an error, print the error and return False
            print(f"Error checking if user is logged in: {e}")
            return False
    
    def remove_logged_in_user(self, player_id): # remove the player_id from the logged_in_users table
        self.cur.execute("DELETE FROM logged_in_users WHERE user_id = %s", (player_id,))
        self.conn.commit()

    def remove_player_points(self, value, player_id):
        try: # remove the value from the player's points in the game_rounds table
            self.cur.execute("UPDATE game_rounds SET rounds_won = rounds_won - %s WHERE player_id = %s", (value, player_id))
            self.conn.commit()
        except Exception as e:
            print(f"Error removing player points: {e}")
            self.conn.rollback()
            raise

    def close(self): # close the cursor and connection to the database
        self.cur.close()
        self.conn.close()
