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
            if card_values[hand[1][1:]] in [8, 9, 0]:
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
def predict_winner(deck, player_hand, banker_hand, shown_cards):
    # Logic:
    #   - Simulate the draws based on baccarat rules for both player and banker.
    #   - Count favorable cards (higher than the final hand value) for each side.
    #   - Predict the winner based on the higher favorable card count.

    player_hand = draw_third_card(player_hand.copy(), deck.copy(), 'player')  # Simulate player's draw
    player_value = calculate_value(player_hand)
    
    banker_hand = draw_third_card(banker_hand.copy(), deck.copy(), 'banker')  # Simulate banker's draw
    banker_value = calculate_value(banker_hand)

    player_advantage = 0
    banker_advantage = 0

    for card in deck:
        if card not in shown_cards:
            card_value = card_values[card[1:]]
            if card_value > player_value:
                player_advantage += 1
            if card_value > banker_value:
                banker_advantage += 1

    if player_advantage > banker_advantage:
        return 'Player'
    elif player_advantage < banker_advantage:
        return 'Banker'
    else:
        return 'Tie'

# Simulate 100 games
def simulate_games(num_games):
    player_wins = 0
    banker_wins = 0
    ties = 0
    prediction_correct = 0
    drawn_cards = [] 
    shown_cards = [] 

    # Track consecutive correct and incorrect predictions
    consecutive_correct = 0
    consecutive_incorrect = 0
    max_consecutive_correct = 0
    max_consecutive_incorrect = 0

    # Track predictions for Player and Banker
    player_predictions_correct = 0
    banker_predictions_correct = 0

    for _ in range(num_games):
        deck = create_deck()
        player_hand, banker_hand = deal_cards(deck)
        drawn_cards.extend(player_hand + banker_hand)
        shown_cards.extend(player_hand + banker_hand)  

        # Play a round and get the actual winner
        actual_winner = play_round(deck)

        # Predict the winner
        predicted_winner = predict_winner(deck, player_hand, banker_hand, shown_cards)

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
            # Update predictions for Player/Banker based on the actual winner
            if actual_winner == 'Player':
                player_predictions_correct += 1
            elif actual_winner == 'Banker':
                banker_predictions_correct += 1
        else:
            consecutive_incorrect += 1
            consecutive_correct = 0
            max_consecutive_incorrect = max(max_consecutive_incorrect, consecutive_incorrect)

        # Remove drawn cards from deck for next round
        drawn_cards = []
        shown_cards = [] 

    print(f"Player wins: {player_wins}")
    print(f"Banker wins: {banker_wins}")
    print(f"Ties: {ties}")
    print(f"Total Predictions Correct: {prediction_correct} out of {num_games} games")
    print(f"Player Predictions Correct: {player_predictions_correct}")
    print(f"Banker Predictions Correct: {banker_predictions_correct}")
    print(f"Prediction accuracy: {prediction_correct / num_games * 100:.2f}%")
    print(f"Max consecutive correct predictions: {max_consecutive_correct}")
    print(f"Max consecutive incorrect predictions: {max_consecutive_incorrect}")

# Run the simulation
simulate_games(100)