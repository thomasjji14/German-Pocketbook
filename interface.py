import argparse
from tkinter import *
from frames import *
from fileManager import getFile

def main():
    # Gets the word from the CLI
    parser = argparse.ArgumentParser()
    parser.add_argument("word", nargs = '?')
    args = parser.parse_args()
    word = args.word if args.word is not None else ""

    base = Tk()

    base.title("German Pocketbook")
    base.geometry('600x300')
    base.minsize(600, 300)

    p = Pocketbook(base, word)
    p.pack(expand = True, fill = BOTH)

    base.mainloop()

class Pocketbook(Frame):
    def __init__(self, base, word):
        super().__init__(base, borderwidth = 0, highlightthickness = 0)

        self._menuFrame = Frame(
            self,
            borderwidth = 0,
            highlightthickness = 0
        )
        self._menuFrame.pack(side = TOP, anchor = W)

        # Keyboard bindings as shortcuts
        self._menuFrame.bind_all("<Control-Key-1>",
                                 lambda event: self._dickFocus())
        self._menuFrame.bind_all("<F1>",
                                 lambda event: self._dickFocus())
        self._menuFrame.bind_all("<Control-Key-2>",
                                 lambda event: self._deepFocus())
        self._menuFrame.bind_all("<F2>",
                                 lambda event: self._deepFocus())

        # Build selection panel
        self._dictccIcon = PhotoImage(file = getFile("images/dictccIcon.png"))
        self._dickButton = Button(
            self._menuFrame,
            command = self._dickFocus,
            image = self._dictccIcon
        )
        self._dickButton.grid(column = 0, row = 0, sticky = W)
        self._deepIcon = PhotoImage(file = getFile(
                                        "images/translatorIcon.png"))
        self._deepButton = Button(
            self._menuFrame,
            image = self._deepIcon,
            command = self._deepFocus
        )
        self._deepButton.grid(column = 1, row = 0, sticky = W)

        # Holds the translator tab (no other function)
        self._genericBottomFrame = Frame(
            self,
            borderwidth = 0,
            highlightthickness = 0
        )
        self._genericBottomFrame.pack(
            side = BOTTOM,
            expand = True,
            fill = BOTH
        )
        self._genericBottomFrame.grid_propagate(False)
        self._genericBottomFrame.grid_rowconfigure(0, weight = 1)
        self._genericBottomFrame.grid_columnconfigure(0, weight = 1)

        # Dict.cc
        self._dictFrame = dictionaryFrame(self._genericBottomFrame)
        self._dictFrame.grid(column = 0, row = 0, sticky = NSEW)

        # Translator
        self._translationFrame = translatorFrame(self._genericBottomFrame)
        self._translationFrame.grid(column = 0, row = 0, sticky = NSEW)

        # Makes a guess for what the use wants to see based on the word
        if word.strip().count(" ") <= 1 or len(word) < 3:
            self._dictFrame.provideTranslation(word)
            self._dickFocus()
        else:
            self._translationFrame.provideTranslation(word)
            self._deepFocus()

    def _dickFocus(self) -> None:
        """Forces dickFrame on screen."""
        self._translationFrame.grid_forget()
        self._dictFrame.grid(row = 0, column = 0, sticky = NSEW)

    def _deepFocus(self) -> None:
        """Forces comparisonFrame on screen."""
        self._dictFrame.grid_forget()
        self._translationFrame.grid(row = 0, column = 0, sticky = NSEW)

if __name__ == "__main__":
    main()