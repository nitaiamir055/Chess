from tkinter import *
from tkinter import messagebox


class NotYourTurn(Exception):
    def __init__(self, *args):
        super().__init__(*args)

    def showMessage(self):
        Tk().wm_withdraw()  # to hide the main window
        messagebox.showinfo('Not your Turn', self.args)


class NoUndo(Exception):
    def __init__(self, *args):
        super().__init__(*args)


class IllegalMove(Exception):
    def __init__(self, *args):
        super().__init__(*args)

    def showMessage(self):
        Tk().wm_withdraw()  # to hide the main window
        messagebox.showinfo('Illegal Move', self.args)


class EndGame(Exception):
    def __init__(self, isWhiteTurn):
        super().__init__()
        self.isWhiteWin = not isWhiteTurn

    def showMessage(self):
        Tk().wm_withdraw()  # to hide the main window
        if self.isWhiteWin:
            messagebox.showinfo('End Game', "white win!")
        else:
            messagebox.showinfo('End Game', "black win!")
