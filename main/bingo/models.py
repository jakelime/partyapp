from django.db import models
from django.db.models import JSONField, IntegerField
import random
import pandas as pd
import logging as lg 

# Create your models here.
class BingoBoard(models.Model):

    board = models.JSONField()
    is_winner = models.BooleanField(default=False)
    df_marked = None  # Not a database field, for temporary storage
    size = 7
    json_str_marked = models.JSONField(null=True, blank=True) # Store marked board data as JSON
    
    def generateBoard(self, size=7, max=120):

        number_list = list(range(1, max+1))
        random.shuffle(number_list)

        board = [([0] * size) for _ in range(size)]
        for i in range(size):
            for j in range(size):
                board[i][j] = number_list.pop()
        self.board = board
    
    def to_dataframe(self):
        return pd.DataFrame(self.board)
    
    def validate_board(
        self, winning_numbers: list, print_marked_board: bool = False
    ) -> 'BingoBoard':  # Use string literal for forward reference
        """
        Validates if the given BingoBoard has a winning line (row, column, or diagonal)
        based on the game's winning numbers, using pandas functions.

        Args:
            winning_numbers (list): A list of the current winning numbers.
            print_marked_board (bool, optional): Whether to print the marked board. Defaults to False.

        Returns:
            BingoBoard: The BingoBoard instance with the 'is_winner' attribute updated.
        """
        if not winning_numbers:
            lg.warning(
                "No winning numbers have been generated yet. Board cannot be validated."
            )
            self.is_winner = False
            return self

        # Convert winning numbers to a set for efficient lookups
        winning_set = set(winning_numbers)

        # Convert the board matrix to a pandas DataFrame
        df_board = self.to_dataframe()

        # Create a boolean DataFrame where True indicates a number is in winning_set
        df_marked = df_board.isin(winning_set)
        self.df_marked = df_marked  # Store marked DataFrame in the board instance
        self.json_str_marked = df_marked.to_json()  # Store marked data as json
        if print_marked_board:
            dfm = df_marked.replace({False: " ", True: "W"})
            lg.info(f"Marked board:\n{dfm}")

        board_size = self.size

        # Check rows: if any row is all True
        if df_marked.all(axis=1).any():
            winning_row_idx = df_marked.all(axis=1).idxmax()
            lg.debug(f"Winning row found: {df_board.loc[winning_row_idx].tolist()}")
            self.is_winner = True
            return self

        # Check columns: if any column is all True
        if df_marked.all(axis=0).any():
            winning_col_idx = df_marked.all(axis=0).idxmax()
            lg.debug(f"Winning column found: {df_board[winning_col_idx].tolist()}")
            self.is_winner = True
            return self

        # Check main diagonal (top-left to bottom-right)
        # Extract the main diagonal as a pandas Series and check if all are True
        main_diag_marked = pd.Series([df_marked.iloc[i, i] for i in range(board_size)])
        if main_diag_marked.all():
            main_diag_numbers = [int(df_board.iloc[i, i]) for i in range(board_size)]
            lg.debug(f"Winning main diagonal found: {main_diag_numbers}")
            self.is_winner = True
            return self

        # Check anti-diagonal (top-right to bottom-left)
        # Extract the anti-diagonal as a pandas Series and check if all are True
        anti_diag_marked = pd.Series(
            [df_marked.iloc[i, board_size - 1 - i] for i in range(board_size)]
        )
        if anti_diag_marked.all():
            anti_diag_numbers = [
                int(df_board.iloc[i, board_size - 1 - i]) for i in range(board_size)
            ]
            lg.debug(f"Winning anti-diagonal found: {anti_diag_numbers}")
            self.is_winner = True
            return self

        # If no winning line is found
        lg.debug("No winning line found on the board.")
        self.is_winner = False
        return self





class winningNumber(models.Model):
    num = IntegerField()
