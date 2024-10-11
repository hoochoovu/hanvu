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
def draw_third_card(hand, deck, role):
    value = calculate_value(hand)
    if role == 'player':
        if value <= 5:
            hand.append(deck.pop())
    elif role == 'banker':
        if value <= 2:
            hand.append(deck.pop())
        elif value == 3:
            if card_values[hand[1][1:]] not in [8]:
                hand.append(deck.pop())
        elif value == 4:
            if card_values[hand[1][1:]] in [2, 3, 4, 5, 6, 7]:
                hand.append(deck.pop())
        elif value == 5:
            if card_values[hand[1][1:]] in [4, 5, 6, 7]:
                hand.append(deck.pop())
        elif value == 6:
            if card_values[hand[1][1:]] in [6, 7]:
                hand.append(deck.pop())
    return hand

# Play a round of baccarat
def play_round(deck):
    player_hand, banker_hand = deal_cards(deck)

    # Player's turn
    player_hand = draw_third_card(player_hand, deck, 'player')
    player_value = calculate_value(player_hand)

    # Banker's turn
    banker_hand = draw_third_card(banker_hand, deck, 'banker')
    banker_value = calculate_value(banker_hand)

    # Determine the winner
    if player_value > banker_value:
        return 'Player'
    elif banker_value > player_value:
        return 'Banker'
    else:
        return 'Tie'

# Predict winner using 100 prisoner problem logic (with full baccarat rules)
def predict_winner(deck, player_hand, banker_hand, shown_cards, loop_index):
    loop_count = len(shown_cards)
    target_card = deck[loop_index % loop_count]
    
    # Check if the predicted card is favorable for Player or Banker
    target_value = card_values[target_card[1:]]
    
    player_value = calculate_value(player_hand)
    banker_value = calculate_value(banker_hand)

    if target_value > player_value and target_value > banker_value:
        return 'Tie'
    elif target_value > player_value:
        return 'Banker'
    elif target_value > banker_value:
        return 'Player'
    else:
        # If the value is the same, base the prediction on card suits or other criteria
        return 'Tie'

# Simulate 100 games
def simulate_games(num_games):
    player_wins = 0
    banker_wins = 0
    ties = 0
    prediction_correct = 0
    shown_cards = [] 
    loop_index = 0  # Track the loop position

    # Track consecutive correct and incorrect predictions
    consecutive_correct = 0
    consecutive_incorrect = 0
    max_consecutive_correct = 0
    max_consecutive_incorrect = 0

    for _ in range(num_games):
        deck = create_deck()
        player_hand, banker_hand = deal_cards(deck)
        shown_cards.extend(player_hand + banker_hand)  

        # Play a round and get the actual winner
        actual_winner = play_round(deck)

        # Predict the winner
        predicted_winner = predict_winner(deck, player_hand, banker_hand, shown_cards, loop_index)
        loop_index += 1  # Update loop position after each round

        # Update win counts
        if actual_winner == 'Player':
            player_wins += 1
        elif actual_winner == 'Banker':
            banker_wins += 1
        else:
            ties += 1

        # Check if prediction is correct and update consecutive counts
        if actual_winner == predicted_winner:
            prediction_correct += 1
            consecutive_correct += 1
            consecutive_incorrect = 0
            max_consecutive_correct = max(max_consecutive_correct, consecutive_correct)
        else:
            consecutive_incorrect += 1
            consecutive_correct = 0
            max_consecutive_incorrect = max(max_consecutive_incorrect, consecutive_incorrect)

        # Clear shown cards for the next round
        shown_cards = [] 

    print(f"Player wins: {player_wins}")
    print(f"Banker wins: {banker_wins}")
    print(f"Ties: {ties}")
    print(f"Total Predictions Correct: {prediction_correct} out of {num_games} games")
    print(f"Prediction accuracy: {prediction_correct / num_games * 100:.2f}%")
    print(f"Max consecutive correct predictions: {max_consecutive_correct}")
    print(f"Max consecutive incorrect predictions: {max_consecutive_incorrect}")

# Run the simulation
simulate_games(1000)
