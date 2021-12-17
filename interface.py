import argparse
from tkinter import *
from frames import *
from fileManager import getFile

def dickFocus():
    # Forces dickFrame on screen
    translationFrame.grid_forget()
    dictFrame.grid(row = 0, column = 0, sticky = NSEW)

def deepFocus():
    # Forces comparisonFrame on screen
    dictFrame.grid_forget()
    translationFrame.grid(row = 0, column = 0, sticky = NSEW)

parser = argparse.ArgumentParser()
parser.add_argument("word", nargs = '?')
args = parser.parse_args()
word = args.word if args.word is not None else ""

base = Tk()
base.title("German Pocketbook")
base.geometry('600x300')
base.minsize(600, 300)

pageFrame = Frame(base, borderwidth = 0, highlightthickness = 0)
pageFrame.pack(side = LEFT, expand = True, fill = BOTH)

menuFrame = Frame(pageFrame, borderwidth = 0, highlightthickness = 0)
menuFrame.pack(side = TOP, anchor = W)

dictccIcon = PhotoImage(file = getFile("images/dictccIcon.png"))
dickButton = Button(menuFrame, command = dickFocus, image = dictccIcon)
dickButton.grid(column = 0, row = 0, sticky = W)
deepIcon = PhotoImage(file = getFile("images/translatorIcon.png"))
deepButton = Button(menuFrame, image = deepIcon, command = deepFocus)
deepButton.grid(column = 1, row = 0, sticky = W)

genericBottomFrame = Frame(pageFrame, borderwidth = 0, highlightthickness = 0)
genericBottomFrame.pack(side = BOTTOM, expand = True, fill = BOTH)
genericBottomFrame.grid_propagate(False)
genericBottomFrame.grid_rowconfigure(0, weight = 1)
genericBottomFrame.grid_columnconfigure(0, weight = 1)

# Dict.cc
dictFrame = dictionaryFrame(genericBottomFrame)
dictFrame.grid(column = 0, row = 0, sticky = NSEW)

translationFrame = translatorFrame(genericBottomFrame)
translationFrame.grid(column = 0, row = 0, sticky = NSEW)

# approximate number of words (1 + numSpaces)
# doesn't activate both at run for faster startup
if word.strip().count(" ") <= 1 or len(word) < 3:
    dictFrame.provideTranslation(word)
    dickFocus()
else:
    translationFrame.provideTranslation(word)
    deepFocus()

# Keyboard shortcuts to switch tabs
menuFrame.bind_all("<Control-Key-1>", lambda event: dickFocus())
menuFrame.bind_all("<F1>", lambda event: dickFocus())
menuFrame.bind_all("<Control-Key-2>", lambda event: deepFocus())
menuFrame.bind_all("<F2>", lambda event: deepFocus())

base.mainloop()