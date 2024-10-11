import random

# Define card values
card_values = {
    'A': 1,
    '2': 2,
    '3': 3,
    '4': 4,
    '5': 5,
    '6': 6,
    '7': 7,
    '8': 8,
    '9': 9,
    '10': 0,
    'J': 0,
    'Q': 0,
    'K': 0
}

# Create a deck of 8 decks
def create_deck():
    deck = []
    for suit in ['C', 'D', 'H', 'S']:
        for rank in ['A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K']:
            deck.extend([suit + rank] * 8)  # 8 decks of each card
    random.shuffle(deck)
    return deck

# Calculate hand value
def calculate_value(hand):
    value = sum(card_values[card[1:]] for card in hand)
    if value > 9:
        value %= 10
    return value

# Deal cards
def deal_cards(deck):
    player_hand = [deck.pop(), deck.pop()]
    banker_hand = [deck.pop(), deck.pop()]
    return player_hand, banker_hand

# Determine if a player or banker should draw a third card
def draw_third_card(hand, deck):
    value = calculate_value(hand)
    if value <= 5:
        hand.append(deck.pop())
    return hand

# Play a round of baccarat
def play_round(deck):
    player_hand, banker_hand = deal_cards(deck)

    # Player's turn
    player_hand = draw_third_card(player_hand, deck)
    player_value = calculate_value(player_hand)

    # Banker's turn
    banker_value = calculate_value(banker_hand)
    if banker_value <= 5:
        banker_hand = draw_third_card(banker_hand, deck)
        banker_value = calculate_value(banker_hand)

    # Determine the winner
    if player_value > banker_value:
        return 'Player'
    elif banker_value > player_value:
        return 'Banker'
    else:
        return 'Tie'

# Simulate 100 games
def simulate_games(num_games):
    player_wins = 0
    banker_wins = 0
    ties = 0

    for _ in range(num_games):
        deck = create_deck()
        winner = play_round(deck)
        if winner == 'Player':
            player_wins += 1
        elif winner == 'Banker':
            banker_wins += 1
        else:
            ties += 1

    print(f"Player wins: {player_wins}")
    print(f"Banker wins: {banker_wins}")
    print(f"Ties: {ties}")

# Run the simulation
simulate_games(100)