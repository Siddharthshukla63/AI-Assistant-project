import tkinter as tk
from tkinter import messagebox
import random

class TicTacToeGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Tic-Tac-Toe")
        self.mode = None # 'pvp' or 'pvc'
        self.current_player = 'O' # Human always starts as O
        self.board = [str(i+1) for i in range(9)]
        self.buttons = []
        
        self.setup_menu()

    def setup_menu(self):
        """Creates the initial selection screen."""
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack(pady=20)
        
        tk.Label(self.menu_frame, text="Select Game Mode", font=('Arial', 20, 'bold')).pack(pady=10)
        
        tk.Button(self.menu_frame, text="Player vs Player", width=50, 
                  command=lambda: self.start_game('pvp')).pack(pady=5)
        
        tk.Button(self.menu_frame, text="Player vs Computer", width=50, 
                  command=lambda: self.start_game('pvc')).pack(pady=5)

    def start_game(self, mode):
        """Clears the menu and builds the game grid."""
        self.mode = mode
        self.menu_frame.destroy()
        
        # Grid Frame
        self.grid_frame = tk.Frame(self.root)
        self.grid_frame.pack()

        for i in range(9):
            btn = tk.Button(self.grid_frame, text="", font=('Arial', 20), width=7, height=5,
                            command=lambda i=i: self.on_click(i))
            btn.grid(row=i//3, column=i%3)
            self.buttons.append(btn)

        # Reset Button
        tk.Button(self.root, text="Restart Game", command=self.reset_game).pack(pady=10)

        # If PVC, Computer makes the first move in the middle (per your original main.py)
        if self.mode == 'pvc':
            self.board[4] = 'X'
            self.buttons[4].config(text='X', state='disabled', disabledforeground="red")

    def on_click(self, index):
        if self.board[index] not in ['O', 'X']:
            # Human move (or Player 1 move)
            self.make_move(index, self.current_player)
            
            if not self.check_game_over(self.current_player):
                if self.mode == 'pvc':
                    self.root.after(500, self.computer_move)
                else:
                    # Switch player for PvP
                    self.current_player = 'X' if self.current_player == 'O' else 'O'

    def computer_move(self):
        free_fields = [i for i, val in enumerate(self.board) if val not in ['O', 'X']]
        if free_fields:
            move = random.choice(free_fields)
            self.make_move(move, 'X')
            self.check_game_over('X')

    def make_move(self, index, sgn):
        self.board[index] = sgn
        color = "blue" if sgn == 'O' else "red"
        self.buttons[index].config(text=sgn, state='disabled', disabledforeground=color)

    def check_game_over(self, sgn):
        victor = self.victory_for(sgn)
        if victor:
            winner_name = "Player O" if sgn == 'O' else ("Computer" if self.mode == 'pvc' else "Player X")
            messagebox.showinfo("Game Over", f"{winner_name} wins!")
            self.reset_game()
            return True
        elif all(x in ['O', 'X'] for x in self.board):
            messagebox.showinfo("Game Over", "It's a Tie!")
            self.reset_game()
            return True
        return False

    def victory_for(self, sgn):
        win_coords = [(0,1,2), (3,4,5), (6,7,8), (0,3,6), (1,4,7), (2,5,8), (0,4,8), (2,4,6)]
        for a, b, c in win_coords:
            if self.board[a] == self.board[b] == self.board[c] == sgn:
                return True
        return None

    def reset_game(self):
        """Clears the window and goes back to the selection menu."""
        for widget in self.root.winfo_children():
            widget.destroy()
        self.__init__(self.root)

if __name__ == "__main__":
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()