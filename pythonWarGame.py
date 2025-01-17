import random
import time
from database import Database
import os

class Card: # this class is used to create a card object
    suits = ['Hearts','Diamonds','Clubs','Spades'] # list of card suits
    values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'Jack', 'Queen', 'King', 'Ace'] # list of card values
    Jokers = ['Joker'] # list of jokers
    def __init__(self, suit=None, value=None):
        # Initialize the card with a suit and value
        self.suit = suit
        self.value = value
    
class Deck:
    def __init__(self):
        # Initialize the deck with 54 cards, always including 2 jokers
        self.cards = [Card(suit, value) for suit in Card.suits for value in Card.values]
        self.cards.extend([Card('Joker', 'Joker'), Card('Joker', 'Joker')]) # add jokers to the deck
        # Shuffle the deck to randomize the order of the cards
        random.shuffle(self.cards)

    def draw(self):
        # Draw a card from the deck (remove and return the last card in the list)
        return self.cards.pop() if self.cards else None
    
class Player:
    # Initialize the player with a name and an empty hand
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.id = None
        self.joker_points = 0

    def draw_card(self):
        # Draw a card from the player's hand (remove and return first card in the list)
        return self.hand.pop(0) if self.hand else None
    
    def add_cards(self, cards):
        # Add a list of cards to the player's hand
        self.hand.extend(cards)
    
    def has_cards(self):
        # Check if the player has any cards in their hand
        return len(self.hand) > 0

#from curses_functions import json_handler, curses_handler

class WarGame:
    def __init__(self, player1_id, player2_id):
        self.db = Database(dbname='wargame', user='postgres', password='post', host='localhost')
        # Initialize the game with two players and a deck of cards
        self.deck = Deck()
        self.player1 = Player(self.db.get_player_name(player1_id)) # get and assign the payer name to the object
        self.player2 = Player(self.db.get_player_name(player2_id))
        self.player1.id = player1_id # assign the player id to the object
        self.player2.id = player2_id
        self.game_id = self.db.create_game(self.player1.id, self.player2.id) # create a new game in the database
        self.db.create_game_round(self.game_id, self.player1.id) # create a game round for player 1
        self.db.create_game_round(self.game_id, self.player2.id) # create a game round for player 2
        self.deal_cards() # deal the cards to the players
        self.player_points = [0,0] # set player points to 0 at the start of the game
        self.player1.joker_points = 0 # used to keep track of the points lost to the joker
        self.player2.joker_points = 0
    def deal_cards(self):
        # Deal cards to the players in alternating order
        while self.deck.cards: 
            self.player1.add_cards([self.deck.draw()]) # draw a card from the deck and add it to player 1
            self.player2.add_cards([self.deck.draw()]) # draw a card from the deck and add it to player 2

    def draw_card_ascii(self, card): # this function is used to draw the card in ascii art
        suits_symbols = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠', 'Joker': 'j'}
        royal_values = {'Jack': 'J', 'Queen': 'Q', 'King': 'K', 'Ace': 'A', 'Joker': 'j'}
        value = card.value
        suit = suits_symbols[card.suit] 
        if value in royal_values: # if the value is a royal value, assign the value to the royal value
            value = royal_values[value] 
        card_art = f"""
        ┌─────────┐
        │{value:<2}       │
        │         │
        │    {suit}    │
        │         │
        │       {value:>2}│
        └─────────┘
        """ # ascii art for the card
        return card_art 

    def draw_cards_for_war(self, cards):
        suits_symbols = {'Hearts': '♥', 'Diamonds': '♦', 'Clubs': '♣', 'Spades': '♠', 'Joker': 'j'}
        royal_values = {'Jack': 'J', 'Queen': 'Q', 'King': 'K', 'Ace': 'A', 'Joker': 'j'}
        card = cards[-1]
        value = card.value
        suit = suits_symbols[card.suit]
        if value in royal_values:
            value = royal_values[value]

        card_art = f"""
        ┌─────┌─────┌─────┌─────────┐
        │░░░░░|░░░░░│░░░░░│{value:<2}       │
        │░░░░░|░░░░░│░░░░░|         │
        │░░░░¤|░░░░¤│░░░░¤│    {suit}    │
        │░░░░░|░░░░░│░░░░░|         │
        │░░░░░|░░░░░│░░░░░│       {value:>2}│
        └─────└─────└─────└─────────┘
        """ # ascii art for the war cards
        return card_art
    
    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear') # clear the terminal screen

    def play_round(self):
        # play a single round of the game
        if not self.player1.has_cards() or not self.player2.has_cards():
            return

        # Draw a card from each player's hand
        p1_card = self.player1.draw_card()
        p2_card = self.player2.draw_card()

        ## funky graphicial stuff here. to show the cards being played

        # Display the cards played by each player
        print(f"{self.player1.name}")
        print(self.draw_card_ascii(p1_card))
        print(f"{self.player2.name}")
        print(self.draw_card_ascii(p2_card))
        time.sleep(1)

        if p1_card.value == 'j' or p1_card.value == 'Joker':
            # self.joker_card_curses(self.player1.id, self.player1.hand)
            print(f"The Joker has cursed you! {self.player1.name}")
            print("Reduce points by 3")
            self.player1.joker_points += 3
            # self.db.remove_player_points("3", self.player1.id)
        if p2_card.value == 'j' or p2_card.value == 'Joker':
            # self.joker_card_curses(self.player2.id, self.player2.hand)
            print(f"The Joker has cursed you! {self.player2.name}")
            print("Reduce points by 3")
            self.player2.joker_points += 3
            # self.db.remove_player_points("3", self.player2.id)
        
        # Compare the cards and add them to the winner's hand
        print(p1_card.value < p2_card.value)
        
        if p2_card.value == 'Joker' or (p1_card.value > p2_card.value and p1_card.value != 'Joker'):
            ## comparison is buggy 2 > 10 bug
            self.player1.add_cards([p1_card, p2_card])
            self.player_points[0] += 1 # add a point to player 1
            print(f"{self.player1.name} wins the round, {self.player_points[0]} points")
            self.db.update_round_stats(self.game_id, self.player1.id, 'rounds_won')
            self.db.update_round_stats(self.game_id, self.player2.id, 'rounds_lost')
            
            time.sleep(5)
            self.clear_terminal()
        elif p1_card.value == 'Joker' or (p2_card.value > p1_card.value and p2_card.value != 'Joker'):
            
            self.player2.add_cards([p1_card, p2_card])
            self.player_points[1] += 1 # add a point to player 2
            print(f"{self.player2.name} wins the round, {self.player_points[1]} points")
            # update the round stats for the player, 1 for win, 0 for loss
            self.db.update_round_stats(self.game_id, self.player2.id, 'rounds_won')
            self.db.update_round_stats(self.game_id, self.player1.id, 'rounds_lost')

            time.sleep(5) # wait for 5 seconds to let the players see the results
            self.clear_terminal() # clear the terminal screen to show the next round
        else:
            print("War!") # if the cards are equal, start a war
            time.sleep(1)
            # Handle a war if the cards are equal
            self.handle_war([p1_card], [p2_card])
    
    def handle_war(self, p1_pile, p2_pile):
        # Handle a war by drawing four cards from each player's hand
        if len(self.player1.hand) < 4 or len(self.player2.hand) < 4:
            return
        
        # Draw four cards from each player's hand
        p1_pile.extend([self.player1.draw_card() for _ in range(4)])
        p2_pile.extend([self.player2.draw_card() for _ in range(4)])

        ## more funky graphical stuff here showing the cards being played for war

        # Display the cards played by each player
        print(f"{self.player1.name}")
        print(self.draw_cards_for_war(p1_pile), "\n")
        print(f"{self.player2.name}")
        print(self.draw_cards_for_war(p2_pile), "\n")
        time.sleep(1)

        if p1_pile[-1].value == 'j' or p1_pile[-1].value == 'Joker':
            # self.joker_card_curses(self, self.player1.id, self.player1.hand)
            print("The Joker has cursed you!")
            print(f"Reduce points by 3")
            self.player1.joker_points += 3
            # self.db.remove_player_points("3", self.player1.id)
        if p2_pile[-1].value == 'j' or p2_pile[-1].value == 'Joker':
            # self.joker_card_curses(self, self.player2.id, self.player2.hand)
            print("The Joker has cursed you!")
            print(f"Reduce points by 3")
            self.player2.joker_points += 3
            # self.db.remove_player_points("3", self.player2.id)
        
        # Compare the last card drawn by each player
        # depending on the comparison, add the cards to the winner's hand
        if p2_pile[-1].value == 'Joker' or (p1_pile[-1].value > p2_pile[-1].value and p1_pile[-1].value != 'Joker'):
            self.player1.add_cards(p1_pile + p2_pile)
            self.db.update_round_stats(self.game_id, self.player1.id, 'rounds_won') # player 1 wins the war
            self.db.update_round_stats(self.game_id, self.player2.id, 'rounds_lost') # player 2 loses the war
            self.player_points[0] += 1 # add a point to player 1
            print(f"{self.player1.name} wins the war, {self.player_points[0]} points")

            time.sleep(3)
            self.clear_terminal()
        elif p1_pile[-1].value == 'Joker' or (p2_pile[-1].value > p1_pile[-1].value and p2_pile[-1].value != 'Joker'):
            self.player2.add_cards(p1_pile + p2_pile)
            self.db.update_round_stats(self.game_id, self.player2.id, 'rounds_won') # player 2 wins the war
            self.db.update_round_stats(self.game_id, self.player1.id, 'rounds_lost') # player 1 loses the war
            self.player_points[1] += 1 # add a point to player 2
            print(f"{self.player2.name} wins the war, {self.player_points[1]} points")

            time.sleep(3)
            self.clear_terminal()
        else:
            print("War continues!")
            # Continue the war if the cards are equal
            self.handle_war(p1_pile, p2_pile)

    def play_game(self):
        # Play the game until one player runs out of cards
        round_counter = 0
        while self.player1.has_cards() and self.player2.has_cards():
            round_counter += 1
            print(f"\nRound {round_counter}")
            self.play_round()
            # Exit game after 52 rounds to avoid infinite loop
            if round_counter == 52: # handle the case where the game goes on for too long, (set by user, default is 52 rounds)
                ## get rounds won by each player
                rounds = self.db.get_game_rounds(self.game_id)

                # add the number of cards in each player's hand to the rounds won by each player, 1 card = 1 round won/point
                player1_points = rounds[0][1] + len(self.player1.hand)
                player2_points = rounds[1][1] + len(self.player2.hand)
                p1_final_points = player1_points - self.player1.joker_points
                p2_final_points = player2_points - self.player2.joker_points
                if player1_points <= 0: player1_points = 0
                if player2_points <= 0: player2_points = 0

                print(f"\nGame ended after 52 rounds")
                print(f"\n{self.player1.name} has {player1_points} points, losing {self.player1.joker_points} points to the Joker\nLeaving {p1_final_points} points")
                print(f"{self.player2.name} has {player2_points} points, losing {self.player2.joker_points} points to the Joker\nLeaving {p2_final_points} points")

                if p1_final_points > p2_final_points:
                    print(f"\n{self.player1.name} wins the game!")

                    self.db.update_player_stats(self.player1.id, 'games_won')
                    self.db.update_player_stats(self.player2.id, 'games_lost')

                    winner_id = self.player1.id
            
                elif p2_final_points > p1_final_points:
                    print(f"\n{self.player2.name} wins the game")

                    self.db.update_player_stats(self.player2.id, 'games_won')
                    self.db.update_player_stats(self.player1.id, 'games_lost')

                    winner_id = self.player2.id
                
                else:
                    print("The game is a draw")
                    winner_id = None

                self.db.update_player_at_game_end(self.player1.id, 'rounds_won', rounds[0][1])
                self.db.update_player_at_game_end(self.player2.id, 'rounds_won', rounds[1][1])
                ## add more stats for player tracking(total points, average points per game, etc)

                self.db.record_game(self.game_id, winner_id)
                time.sleep(2)
                break

        # Display the winner of the game if one player runs out of cards
        if self.player1.has_cards():
            print(f"\n{self.player1.name} wins the game!")
            self.db.update_player_stats(self.player1.id, 'games_won')
            self.db.update_player_stats(self.player2.id, 'games_lost')
            winner_id = self.player1.id
            time.sleep(1)
        elif self.player2.has_cards():
            print(f"\n{self.player2.name} wins the game")
            self.db.update_player_stats(self.player2.id, 'games_won')
            self.db.update_player_stats(self.player1.id, 'games_lost')
            winner_id = self.player2.id
            time.sleep(1)
        else:
            print("The game is a draw")
            winner_id = None
        
        self.db.record_game(self.game_id, winner_id) # record the game in the database
        time.sleep(2)

    def __del__(self): # close the database connection when the object is deleted
        self.db.close() 
