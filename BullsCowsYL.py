"""
Cows and Bulls Game with Information Theory Analysis
Demonstrates information theory concepts through simple calculations.

by Yoonki Lee(UFID 61615545)
for EGN6933 Exam III, 2024 Fall

Due Date : 2024-12-01
"""

import random
from math import log2


class BullsCows:
    def __init__(self):
        self.possible_combinations = self.generate_all_numbers()
        self.secret = random.choice(self.possible_combinations)
        self.guesses = []
        self.initial_entropy = self.calculate_entropy()
        # self.secret = "3456"  # TEST

    def generate_all_numbers(self):
        """
        Generate all possible 4-digit numbers with no repeating digits.

        1. First digit: 0-9 (10 choices)
        2. Second digit: 0-9 except first (9 choices)
        3. Third digit: remaining 8 choices
        4. Fourth digit: remaining 7 choices

        Total possibilities: 10 * 9 * 8 * 7 = 5040

        :return: list: All valid 4-digit numbers as strings
        """

        numbers = []  # empty list

        for d1 in range(10):  # First digit: 0-9
            for d2 in range(10):  # Second digit: 0-9
                if d2 != d1:  # Skip if same as first digit
                    for d3 in range(10):  # Third digit: 0-9
                        if d3 != d1 and d3 != d2:  # Skip if same as previous digits
                            for d4 in range(10):  # Fourth digit: 0-9
                                if d4 != d1 and d4 != d2 and d4 != d3:  # Skip if same as previous digits
                                    numbers.append(f"{d1}{d2}{d3}{d4}")

        return numbers

    def calculate_entropy(self):
        """
        Calculate entropy of the current game state(remaining possibilities).
        
        For uniform distribution over n possibilities, entropy = log2(n)

        :return: float: Entropy in bits
        """
        n = len(self.possible_combinations)
        if n == 0:
            return 0
        p = 1 / n  # Uniform distribution
        return n * p * log2(1 / p)  # equals log2(n)

    def get_feedback(self, guess):
        """
        Calculate bulls (correct position) and cows (wrong position) for a guess.

        :param guess: The guess number entered by the user
        :return: tuple: (bulls, cows) counts
        """

        # The sum of the cases where g and s are the same in each digit
        bulls = sum(1 for g, s in zip(guess, self.secret) if g == s)
        # print(bulls)

        # (The sum of the cases where g is in secret number) - bulls
        cows = sum(1 for g in guess if g in self.secret) - bulls
        # print(cows)

        return bulls, cows

    def evaluate_possible_secret(self, guess, possible_secret):
        """
        Calculate bulls (correct position) and cows (wrong position) for a guess with possible secret.

        :param guess: The guess number entered by the user
        :param possible_secret: possible secret
        :return: tuple: (bulls, cows) counts
        """

        # The sum of the cases where g and s are the same in each digit
        bulls = sum(1 for g, s in zip(guess, possible_secret) if g == s)
        # print(bulls)

        # (The sum of the cases where g is in secret number) - bulls
        cows = sum(1 for g in guess if g in possible_secret) - bulls
        # print(cows)

        return bulls, cows

    def calculate_mutual_information(self, guess):
        """
        Calculate mutual information between a potential guess and secret.

        I(X;Y) = H(X) - H(X|Y)
        Where:
        - X is the secret number
        - Y is the feedback from the guess

        :param guess: The guess number entered by the user
        :return: float: Mutual information in bits
        """

        current_entropy = self.calculate_entropy()
        if current_entropy == 0:
            return 0

        # Count how many possibilities lead to each feedback pattern(dictionary with key as tuple)
        feedback_counts = {}
        total = len(self.possible_combinations)

        for possible_secret in self.possible_combinations:
            feedback = self.evaluate_possible_secret(guess, possible_secret)
            feedback_counts[feedback] = feedback_counts.get(feedback, 0) + 1

        # Calculate expected conditional entropy H(X|Y)
        conditional_entropy = 0
        for count in feedback_counts.values():
            if count > 0:
                prob_feedback = count / total
                entropy_given_feedback = log2(count)
                conditional_entropy += prob_feedback * entropy_given_feedback

        # Mutual information is the difference
        return current_entropy - conditional_entropy

    def update_possibilities(self, guess, bulls, cows):
        """
        Update possible combinations based on feedback(bulls and cows).

        :param guess: The guess number entered by the user
        :param bulls: The feedback result of bulls
        :param cows: The feedback result of cows
        """
        # Leave only numbers with the same combination as the feedback result.
        self.possible_combinations = [
            possible_secret for possible_secret in self.possible_combinations
            if self.evaluate_possible_secret(guess, possible_secret) == (bulls, cows)
        ]

    def suggest_guess(self):
        """
        Suggest the next guess number with mutual information.
        The higher mutual information, the more likely the suggestion is correct.

        :return: str: suggestion number
        """

        if not self.possible_combinations:
            return None

        best_guess = None
        max_info = -1

        # candidates = self.possible_combinations
        candidates = self.possible_combinations[:500]  # check only first 500 numbers for efficiency

        for guess in candidates:
            info = self.calculate_mutual_information(guess)
            if info > max_info:
                max_info = info
                best_guess = guess

        return best_guess

    def make_guess(self, guess):
        """
        Process a guess and return feedback with entropy information.

        :param guess: The guess number entered by the user
        :return: dict: bulls, cows, entropy, mutual information and suggestion
        """

        if len(guess) != 4 or len(set(guess)) != 4 or not guess.isnumeric():
            return "Invalid guess. Please enter 4 unique digits."

        bulls, cows = self.get_feedback(guess)
        self.guesses.append((guess, bulls, cows))

        # Calculate entropy and information metrics
        previous_entropy = self.calculate_entropy()
        mutual_info = self.calculate_mutual_information(guess)

        self.update_possibilities(guess, bulls, cows)
        current_entropy = self.calculate_entropy()

        # Get suggestion for next guess
        suggested_guess = self.suggest_guess() if bulls < 4 else None

        return {
            'bulls': bulls,
            'cows': cows,
            'previous_entropy': previous_entropy,
            'current_entropy': current_entropy,
            'mutual_information': mutual_info,
            'remaining_possibilities': len(self.possible_combinations),
            'suggested_next_guess': suggested_guess,
        }


def play_game():
    """
    Main function to play the Bulls and Cows game
    """

    game = BullsCows()
    print("===========================================================")
    print("Welcome to Bulls and Cows game with Information Theory!")
    print("Guess the 4-digit number. Each digit must be unique.")
    print("===========================================================")

    # choose whether if user get hint or not
    suggestion_yn = input("\nWant to get suggestion(hint)? (y/n)")

    # print initial information
    print(f"\nInitial possibilities: {len(game.possible_combinations)}")
    print(f"Initial entropy: {game.initial_entropy:.2f} bits")

    while True:
        guess = input("\nEnter your guess (4 unique digits, 'exit' or 'quit' to exit) : ")
        if guess == 'quit' or guess == 'exit':
            print(f"The secret number: {game.secret}")
            break

        result = game.make_guess(guess)

        # error handling
        if isinstance(result, str):
            print(result)
            continue

        print(f"\nBulls: {result['bulls']}, Cows: {result['cows']}")
        print(f"Previous entropy: {result['previous_entropy']:.2f} bits")
        print(f"Current entropy: {result['current_entropy']:.2f} bits")
        print(f"Mutual information of this guess: {result['mutual_information']:.2f} bits")
        print(f"Remaining possibilities: {result['remaining_possibilities']}")

        if result['suggested_next_guess'] and suggestion_yn.lower() == 'y':
            suggested = result['suggested_next_guess']
            print(f"★Suggested next guess: {suggested}")

            if len(game.possible_combinations) < 10:
                print(f"★Almore There!! {game.possible_combinations}")

        if result['bulls'] == 4:
            print("\nCongratulations! You win!")
            break


if __name__ == '__main__':
    play_game()
