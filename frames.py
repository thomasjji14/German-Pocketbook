from tkinter import *
from tkinter.font import BOLD

from dictcc import Dict
from pydeeplator.deepL import DeepLTranslator
from pydeeplator.deepL import TranslateLanguageEnum, TranslateModeType
from deep_translator import GoogleTranslator
from difflib import SequenceMatcher

from fileManager import getFile

class dictionaryFrame(Frame):
    """ An interface to use with dict.cc. """

    def __init__(self, root):
        super().__init__(root, borderwidth = 0, highlightthickness = 0)
        super().grid_rowconfigure(2, weight = 1)
        super().grid_columnconfigure(0, weight = 1)
        super().grid_columnconfigure(1, weight = 1)

        self._searchText = StringVar()
        self._searchBar = Entry(
            self, textvariable = self._searchText,
            font = ("Arial", 12, BOLD)
        )
        self._searchBar.grid(
            row = 0, column = 0, columnspan = 2, sticky = EW
        )
        self._searchBar.bind(
            "<Return>",
            lambda event : self.provideTranslation(
                self._searchText.get()
            )
        )

        self._englishLabel = Label(
            self,
            text = "",
            font = ("Times New Roman", 1, "bold")
        )
        self._englishLabel.grid(row = 1, column = 0, sticky = W)
        self._germanLabel = Label(
            self,
            text = "",
            font = ("Times New Roman", 1, "bold")
        )
        self._germanLabel.grid(row = 1, column = 1, sticky = W)

        self._sendWordFrame = Frame(
            self, highlightthickness = 0,
            borderwidth = 0
        )
        self._sendWordFrame.grid(row = 2, column = 0, sticky = NSEW)
        self._sendWordFrame.pack_propagate(False)
        self._sendWordListbox = self.dictionaryListBox(
            self._sendWordFrame)
        self._sendWordListbox.pack(expand = True, fill = BOTH)

        self._recieveWordFrame = Frame(
            self,
            highlightthickness = 0,
            borderwidth = 0
        )
        self._recieveWordFrame.grid(row = 2, column = 1, sticky = NSEW)
        self._recieveWordFrame.pack_propagate(False)
        self._recieveListbox = self.dictionaryListBox(
            self._recieveWordFrame)
        self._recieveListbox.pack(expand = True, fill = BOTH)

        # BINDINGS
        self._sendWordListbox.bind(
            "<MouseWheel>",
            lambda event : self._forceScroll(
                event,
                self._recieveListbox,
            )
        )
        self._recieveListbox.bind(
            "<MouseWheel>",
            lambda event : self._forceScroll(
                event,
                self._sendWordListbox
            )
        )

        self._sendWordListbox.bind(
            "<Double-1>",
            lambda event : self._doubleClickAction(
                self._sendWordListbox
            )
        )

        self._recieveListbox.bind(
            "<Double-1>",
            lambda event : self._doubleClickAction(
                self._recieveListbox
            )
        )

    def _doubleClickAction(self, selectedListBox) -> None:
        selectedIndices = selectedListBox.curselection()
        selectedText = selectedListBox.get(selectedIndices)

        # Parsing string to remove tags
        word = ""
        # Remove anything in brackets
        for badCharacter in ['[', '{', '<']:
            while badCharacter in selectedText:
                badCharacterCompliment = chr(ord(badCharacter)+2)
                # Note: [ -> ] and { -> } is a 2 ascii shift
                selectedText = \
                    selectedText[:selectedText.index(badCharacter)] + \
                    selectedText[selectedText.index(badCharacterCompliment)+1:]

        # Don't include any words with commas or periods
        for wordBit in selectedText.split(" "):
            if '.' not in wordBit and ',' not in wordBit:
                word += wordBit + " "
        word = word.strip()

        # Entry bar
        self._searchText.set(word)
        self.provideTranslation(word)

    def provideTranslation(self, textToTranslate) -> None:
        """Updates the frame based on the input text."""
        self._searchText.set(textToTranslate)
        translator = Dict()
        result = translator.translate(
            textToTranslate,
            from_language = "en",
            to_language = "de"
        )

        outputText = ""
        for wordTuple in result.translation_tuples:
            outputText += wordTuple[0] + " | " + wordTuple[1] + "\n"

        if len(outputText) == 0:
            inputText = ("No entries found.",)
            resultText = ("No translations returned.",)
        else:
            inputText = tuple(
                wordTuple[0] for wordTuple in result.translation_tuples
            )
            resultText = tuple(
                wordTuple[1] for wordTuple in result.translation_tuples
            )

        self._sendWordListbox.updateText(inputText)
        self._recieveListbox.updateText(resultText)

    def _forceScroll(self, event, otherListBox) -> None:
        otherListBox.yview_scroll(int(-4*(event.delta/120)), "units")

    def getCurrentText(self) -> str:
        """Returns the search term."""
        return self._searchText.get()

    class dictionaryListBox(Listbox):
        """Custom listbox, with text and color edits"""
        def __init__(self, root, text = "", textFont = ("Arial", 12)):
            self._wordVar = StringVar(value = text)
            super().__init__(
                root,
                highlightthickness = 0,
                borderwidth = 2,
                font = textFont,
                listvariable = self._wordVar,
                height = 2000
            )
            self._checkerRows(text)

        def _checkerRows(self, text):
            """ Invoke every time new rows are made """
            for i in range(0, len(text), 2):
                super().itemconfigure(i, background='#f0f0f0')

        def updateText(self, text):
            self._wordVar.set(text)
            self._checkerRows(text)

class translatorFrame(Frame):
    """ An interface to use with Google Translate/DeepL. """
    def __init__(self, root, textToTranslate = ""):
        super().__init__(root, borderwidth = 1, bg = "gray")
        self._useDeepL = False

        self._translatorMenuPanel = Frame(self)
        self._translatorMenuPanel.pack(side = TOP, fill = X)

        self._originalTextFrame = self.TextFrame(self, lockEntry = False)
        self._originalTextFrame.pack(side = TOP, expand = True, fill = BOTH)

        self._translatedTextFrame = self.TextFrame(self)
        self._translatedTextFrame.pack(side = BOTTOM,
                                        expand = True, fill = BOTH)

        self._languageSwitchText = StringVar()
        self._languageSwitchText.set('? ⥎ ?')
        self._languageSwitchButton = Button(
            self._translatorMenuPanel,
            textvariable = self._languageSwitchText,
            command = self._switchLanguage,
            font = ("Comic Sans MS", 9),
            bg = "light sky blue"
        )
        self._languageSwitchButton.pack(side = LEFT)
        self._doubleSwitchButton = Button(
            self._translatorMenuPanel,
            text = '⮀',
            command = self._switchBoth,
            font = ("Comic Sans MS", 9),
            bg = "lemon chiffon"
        )
        self._doubleSwitchButton.pack(side = LEFT)
        self._textSwitchButton = Button(
            self._translatorMenuPanel,
            text = 'TEXT ⥐ TRANS',
            command = self._switchFields,
            font = ("Comic Sans MS", 9),
            bg = "light sky blue"
        )
        self._textSwitchButton.pack(side = LEFT)

        self._googleIcon = PhotoImage(file = getFile("images/googleIcon.png"))
        self._deepLIcon = PhotoImage(file = getFile("images/deepLIcon.png"))

        self._deepLButton = Button(
            self._translatorMenuPanel,
            image = self._googleIcon,
            command = self._toggleDeepStatus
        )
        self._deepLButton.pack(side = RIGHT)

        self._originalTextFrame.bindText(
            "<Return>",
            lambda event : self.provideTranslation(self.getCurrentText())
        )

        super().bind_all("<F12>", lambda event : self._toggleDeepStatus())
        super().bind_all("<F5>",  lambda event : self._switchBoth())
        super().bind_all("<F6>",  lambda event : self._switchLanguage())
        super().bind_all("<F7>",  lambda event : self._switchFields())

        if len(textToTranslate) != 0:
            self.provideTranslation(textToTranslate)

    def _toggleDeepStatus(self) -> None:
        self._useDeepL = not self._useDeepL
        if self._useDeepL:
            self._deepLButton.configure(image = self._deepLIcon)
        else:
            self._deepLButton.configure(image = self._googleIcon)

    def _switchLanguage(self) -> None:
        currentText = self._languageSwitchText.get()
        language1 = currentText.split(" ")[0]
        language2 = currentText.split(" ")[-1]
        self.provideTranslation(self.getCurrentText(),
                                forceLanguage = (language2, language1))

    def _switchFields(self) -> None:
        # NOTE: needs to preserve current language
        currentText = self._languageSwitchText.get()
        language1 = currentText.split(" ")[0]
        language2 = currentText.split(" ")[-1]
        self.provideTranslation(
            self._translatedTextFrame.getText(),
            forceLanguage = (language1, language2)
        )

    def _switchBoth(self) -> None:
        currentText = self._languageSwitchText.get()
        language1 = currentText.split(" ")[0]
        language2 = currentText.split(" ")[-1]
        self.provideTranslation(
            self._translatedTextFrame.getText(),
            forceLanguage = (language2, language1)
        )

    def provideTranslation(self, textToTranslate, forceLanguage =None) -> None:
        # This is a temporary solution, since there isn't a good way to
        # identify text language (textblob is currently broken)
        if forceLanguage is None:
            # A guess needs to be made if a language isn't stated
            # Translate into both languages, and the more dissimilar
            # result will be the target language.
            germanText = GoogleTranslator(
                source = "english",
                target = "german"
            ).translate(textToTranslate)
            germanSimilarity = SequenceMatcher(
                None, textToTranslate, germanText).ratio()

            englishText = result = GoogleTranslator(
                    source = "german",
                    target = "english"
                ).translate(textToTranslate)
            englishSimilarity = SequenceMatcher(
                None, textToTranslate, englishText).ratio()

            if germanSimilarity < englishSimilarity:
                forceLanguage = ["EN", "DE"]
            else:
                forceLanguage = ["DE", "EN"]


        if self._useDeepL:
            try:
                lang1 = forceLanguage[0].upper()
                lang2 = forceLanguage[1].upper()

                result = DeepLTranslator (
                    translate_str = textToTranslate,
                    source_lang = lang1,
                    target_lang = lang2,
                    translate_mode = TranslateModeType.SENTENCES,
                ).translate()['result']

                self._languageSwitchText.set(lang1 + " ⥎ " + lang2)
            except:
                # note: modifies deepL status to allow for the next if
                # to run
                self._toggleDeepStatus()

        if not self._useDeepL:
            googleLanguageMapping = {
                'en' : "english",
                "EN" : "english",
                'de' : "german",
                "DE" : "german",
            }
            lang1 = forceLanguage[0]
            lang2 = forceLanguage[1]
            result = GoogleTranslator(
                source = googleLanguageMapping[lang1],
                target = googleLanguageMapping[lang2]
            ).translate(textToTranslate)
            self._languageSwitchText.set(lang1 + " ⥎ " + lang2)

        self._originalTextFrame.updateText(textToTranslate)
        self._translatedTextFrame.updateText(result)

    def getCurrentText(self) -> None:
        return self._originalTextFrame.getText()

    class TextFrame(Frame):
        """Custom Frame to allow for updatable text"""
        def __init__(self, root, lockEntry = True):
            super().__init__(root, borderwidth = 0, highlightthickness = 0)
            super().pack_propagate(False)
            self._isLocked = lockEntry
            self._text = Text(
                self,
                height = 100,
                font = ("Times New Roman", 12),
                wrap = WORD
            )
            self._text.insert(END, "")
            self._text.pack(anchor = W, fill = BOTH, side = BOTTOM)
            self._text.configure(state = DISABLED if lockEntry else NORMAL)

        def updateText(self, updatedText) -> None:
            self._text.configure(state = NORMAL)
            self._text.delete("1.0", END)
            self._text.insert(END, updatedText)
            self._text.configure(
                state = DISABLED if self._isLocked else NORMAL)

        def getText(self) -> str:
            return self._text.get("1.0",'end-1c')

        def updateHeaderText(self, text) -> None:
            self._languageHeaderText.set(text)

        def bindText(self, key, binding) -> None:
            self._text.bind(key, binding)