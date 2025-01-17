import pythonWarGame as wg  # import the WarGame class from WarGame.py
from database import Database as db  # import the database class from database.
from user_accounts import UserAccounts, userStatistics  # import the UserAccounts class from user_accounts.py
from time import sleep
import os

class Interface: # this class is used to interact with the user
    def __init__(self):
        self.db = db(dbname="wargame", user="postgres", password="post", host="localhost")
        self.user_accounts = UserAccounts(self.db) # create a new instance of the UserAccounts class
        self.user_stats = userStatistics(self.db) # create a new instance of the userStatistics class

    def login_menu(self): # this function is used to display the login menu
        print("Welcome to War!")
        print("1. Login")
        print("2. Register")
        print("3. Exit")
        choice = (
            input("Enter your choice: ").strip().replace(";$^£&*()+-=[]{}|:<>,./", "")
        )
        return choice

    def main_menu(self): # this function is used to display the main menu
        print("1. Play a game")
        print("2. View stats # work in progress") # feature not implemented
        print("3. Logout")
        choice = (
            input("Enter your choice: ").strip().replace(";$^£&*()+-=[]{}|:<>,./", "")
        )
        return choice

    def play_game_menu(self): # this function is used to display the play game menu
        print("1. Start a new game")
        print("2. Load a saved game# work in progress") # feature not implemented
        print("3. Quit")
        choice = (
            input("Enter your choice: ").strip().replace(";$^£&*()+-=[]{}|:<>,./", "")
        )
        return choice
    
    def filter_input(self, prompt): # this function is used to filter input from the user
        return input(prompt).strip().replace(";$^£&*()+-=[]{}|:<>,./", "")
    
    def clear_terminal(self): # this function is used to clear the terminal
        os.system('cls' if os.name == 'nt' else 'clear')

    # used for leaderboard functions
    def select_and_return_userStats(self, player_id): # this function is used to select and return the user stats
        stats = self.user_stats.get_user_stats(self, player_id)
        usrname, rounds_won, games_won, games_lost = stats # unpack the stats
        print(f"Player: {usrname}")
        print("----------------------")
        print(f"lifetime points: {rounds_won}")
        print(f"Games won: {games_won}")
        print(f"Games lost: {games_lost} \n")

if __name__ == "__main__":
    interface = Interface()

    logged_in = False
    while logged_in == False:
        # print choice for login menu
        choice = interface.login_menu()
        match choice:
            case '1': # login player 1 and player 2
                for _ in range(3):
                    user1 = interface.user_accounts.login(user_number=1)
                    if user1:
                        player1_id, player1_username, player1_email = user1
                        print("Player 1 login successful")
                        break
                    print("Player 1 login attempts remaining: ", 3 - _)
                    if user1 is not None:
                        db.remove_logged_in_user(user1[0])
                    sleep(1)
                    interface.clear_terminal()
                else:
                    print("Player 1 login attempts failed")
                    continue

                for _ in range(3):
                    user2 = interface.user_accounts.login(user_number=2)
                    if user2:
                        player2_id, player2_username, player2_email = user2
                        print("Player 2 login successful")
                        break
                    print("Player 2 login attempts remaining: ", 3 - _)
                    if user2 is not None:
                        db.remove_logged_in_user(user2[0])
                    sleep(2)
                    interface.clear_terminal()
                else:
                    print("Player 2 login attempts failed")
                    db.remove_logged_in_user(player1_id)
                    continue

                logged_in = True # set logged_in to True this will allow the user to access the main menu loop
            case '2': # register player
                for _ in range(3): # loop 3 times for 3 attempts
                    username = interface.filter_input("enter your username: ")
                    email = interface.filter_input("enter your email: ")
                    # add email fomat validation here at later date
                    password = interface.filter_input("enter your password: ")
                    # add password format validation here at later date
                    if interface.user_accounts.register(username, email, password):
                        print("registration successful")
                        break
                    print("registration attempts remaining: ", 2 - _)
                    sleep(2)
                    interface.clear_terminal()
                else:
                    print("registration attempts failed")
                    interface.user_accounts.logout(player1_id, player2_id) # force logout if registration fails
            case '3':
                interface.user_accounts.logout(player1_id, player2_id) # force remove from logged in table on exit

    while logged_in == True: # main menu and game loop
        choice = interface.main_menu()
        match choice:
            case '1':
                choice = interface.play_game_menu()
                match choice:
                    case '1':
                        game = wg.WarGame(player1_id, player2_id)
                        game.play_game()
                    case '2':
                        print("feature not implemented")
                        interface.user_accounts.logout(player1_id, player2_id)
                    case '3':
                        interface.user_accounts.logout(player1_id, player2_id)
            case '2':
                #interface.select_and_return_userStats(player1_id) ~~ this is a work in progress
                #interface.select_and_return_userStats(player2_id) ~~ this is a work in progress
                print("feature not implemented")
                interface.user_accounts.logout(player1_id, player2_id) 
            case '3':
                interface.user_accounts.logout(player1_id, player2_id)