from tkinter import *
from tkinter.font import BOLD

from dictcc import Dict
from pydeeplator.deepL import DeepLTranslator
from pydeeplator.deepL import TranslateLanguageEnum, TranslateModeType
from deep_translator import GoogleTranslator
from textblob import TextBlob

from fileManager import getFile

class dictionaryFrame(Frame):
    def __init__(self, root):
        super().__init__(root, borderwidth = 0, highlightthickness = 0)
        super().grid_rowconfigure(2, weight = 1)
        super().grid_columnconfigure(0, weight = 1)
        super().grid_columnconfigure(1, weight = 1)

        self.__searchText = StringVar()
        self.__searchBar = Entry(
            self, textvariable = self.__searchText,
            font = ("Arial", 12, BOLD)
        )
        self.__searchBar.grid(
            row = 0, column = 0, columnspan = 2, sticky = EW
        )
        self.__searchBar.bind(
            "<Return>",
            lambda event : self.provideTranslation(
                self.__searchText.get()
            )
        )

        self.__englishLabel = Label(
            self,
            text = "",
            font = ("Times New Roman", 1, "bold")
        )
        self.__englishLabel.grid(row = 1, column = 0, sticky = W)
        self.__germanLabel = Label(
            self,
            text = "",
            font = ("Times New Roman", 1, "bold")
        )
        self.__germanLabel.grid(row = 1, column = 1, sticky = W)

        self.__sendWordFrame = Frame(
            self, highlightthickness = 0,
            borderwidth = 0
        )
        self.__sendWordFrame.grid(row = 2, column = 0, sticky = NSEW)
        self.__sendWordFrame.pack_propagate(False)
        self.__sendWordListbox = self.dictionaryListBox(
            self.__sendWordFrame)
        self.__sendWordListbox.pack(expand = True, fill = BOTH)

        self.__recieveWordFrame = Frame(
            self,
            highlightthickness = 0,
            borderwidth = 0
        )
        self.__recieveWordFrame.grid(row = 2, column = 1, sticky = NSEW)
        self.__recieveWordFrame.pack_propagate(False)
        self.__recieveListbox = self.dictionaryListBox(
            self.__recieveWordFrame)
        self.__recieveListbox.pack(expand = True, fill = BOTH)

        # BINDINGS
        self.__sendWordListbox.bind(
            "<MouseWheel>",
            lambda event : self.__forceScroll(
                event,
                self.__recieveListbox
            )
        )
        self.__recieveListbox.bind(
            "<MouseWheel>",
            lambda event : self.__forceScroll(
                event,
                self.__sendWordListbox
            )
        )

        self.__sendWordListbox.bind(
            "<Double-1>",
            lambda event : self.__doubleClickAction(
                event,
                self.__sendWordListbox
            )
        )

        self.__recieveListbox.bind(
            "<Double-1>",
            lambda event : self.__doubleClickAction(
                event,
                self.__recieveListbox
            )
        )

    def __doubleClickAction(self, event, selectedListBox):
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
        self.__searchText.set(word)
        self.provideTranslation(word)

    def provideTranslation(self, textToTranslate):
        self.__searchText.set(textToTranslate)
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

        self.__sendWordListbox.updateText(inputText)
        self.__recieveListbox.updateText(resultText)

    def __forceScroll(self, event, otherListBox):
        otherListBox.yview_scroll(int(-4*(event.delta/120)), "units")

    def getCurrentText(self):
        return self.__searchText.get()

    class dictionaryListBox(Listbox):
        def __init__(self, root, text = "", textFont = ("Arial", 12)):
            self.__wordVar = StringVar(value = text)
            super().__init__(
                root,
                highlightthickness = 0,
                borderwidth = 2,
                font = textFont,
                listvariable = self.__wordVar,
                height = 2000
            )
            self.__checkerRows(text)

        def __checkerRows(self, text):
            """ Invoke every time new rows are made """
            for i in range(0, len(text), 2):
                super().itemconfigure(i, background='#f0f0f0')

        def updateText(self, text):
            self.__wordVar.set(text)
            self.__checkerRows(text)

class translatorFrame(Frame):
    def __init__(self, root, textToTranslate = ""):
        super().__init__(root, borderwidth = 1, bg = "gray")
        self.__useDeepL = False

        self.__translatorMenuPanel = Frame(self)
        self.__translatorMenuPanel.pack(side = TOP, fill = X)

        self.__originalTextFrame = self.TextFrame(self, lockEntry = False)
        self.__originalTextFrame.pack(side = TOP, expand = True, fill = BOTH)

        self.__translatedTextFrame = self.TextFrame(self)
        self.__translatedTextFrame.pack(side = BOTTOM,
                                        expand = True, fill = BOTH)

        self.__languageSwitchText = StringVar()
        self.__languageSwitchText.set('? ⥎ ?')
        self.__languageSwitchButton = Button(
            self.__translatorMenuPanel,
            textvariable = self.__languageSwitchText,
            command = self.__switchLanguage,
            font = ("Comic Sans MS", 9)
        )
        self.__languageSwitchButton.pack(side = LEFT)
        self.__doubleSwitchButton = Button(
            self.__translatorMenuPanel,
            text = '⮀',
            command = self.__switchBoth,
            font = ("Comic Sans MS", 9)
        )
        self.__doubleSwitchButton.pack(side = LEFT)
        self.__textSwitchButton = Button(
            self.__translatorMenuPanel,
            text = 'TEXT ⥐ TRANS',
            command = self.__switchFields,
            font = ("Comic Sans MS", 9)
        )
        self.__textSwitchButton.pack(side = LEFT)

        self.__googleIcon = PhotoImage(file = getFile("images/googleIcon.png"))
        self.__deepLIcon = PhotoImage(file = getFile("images/deepLIcon.png"))

        self.__deepLButton = Button(
            self.__translatorMenuPanel,
            image = self.__googleIcon,
            command = self.__toggleDeepStatus
        )
        self.__deepLButton.pack(side = RIGHT)

        self.__originalTextFrame.bindText(
            "<Return>",
            lambda event : self.provideTranslation(self.getCurrentText())
        )

        super().bind_all("<F12>", lambda event : self.__toggleDeepStatus())
        super().bind_all("<F5>",  lambda event : self.__switchBoth())
        super().bind_all("<F6>",  lambda event : self.__switchLanguage())
        super().bind_all("<F7>",  lambda event : self.__switchFields())

        if len(textToTranslate) != 0:
            self.provideTranslation(textToTranslate)

    def __toggleDeepStatus(self):
        self.__useDeepL = not self.__useDeepL
        if self.__useDeepL:
            self.__deepLButton.configure(image = self.__deepLIcon)
        else:
            self.__deepLButton.configure(image = self.__googleIcon)

    def __switchLanguage(self):
        currentText = self.__languageSwitchText.get()
        language1 = currentText.split(" ")[0]
        language2 = currentText.split(" ")[-1]
        self.provideTranslation(self.getCurrentText(),
                                forceLanguage = (language2, language1))

    def __switchFields(self):
        # NOTE: needs to preserve current language
        currentText = self.__languageSwitchText.get()
        language1 = currentText.split(" ")[0]
        language2 = currentText.split(" ")[-1]
        self.provideTranslation(
            self.__translatedTextFrame.getText(),
            forceLanguage = (language1, language2)
        )

    def __switchBoth(self):
        currentText = self.__languageSwitchText.get()
        language1 = currentText.split(" ")[0]
        language2 = currentText.split(" ")[-1]
        self.provideTranslation(
            self.__translatedTextFrame.getText(),
            forceLanguage = (language2, language1)
        )

    def provideTranslation(self, textToTranslate, forceLanguage = None):
        if self.__useDeepL:
            try:
                if forceLanguage is None:
                    languageGuess = TextBlob(textToTranslate).detect_language()

                    if languageGuess == "en":
                        result = DeepLTranslator(
                            translate_str= textToTranslate,
                            target_lang=TranslateLanguageEnum.DE,
                            translate_mode=TranslateModeType.SENTENCES,
                            ).translate()['result']
                        self.__languageSwitchText.set("EN" + " ⥎ " + "DE")
                    else:
                        result = DeepLTranslator(
                            translate_str= textToTranslate,
                            target_lang=TranslateLanguageEnum.EN,
                            translate_mode=TranslateModeType.SENTENCES,
                            ).translate()['result']
                        self.__languageSwitchText.set("DE" + " ⥎ " + "EN")
                else:
                    lang1 = forceLanguage[0].upper()
                    lang2 = forceLanguage[1].upper()

                    result = DeepLTranslator (
                        translate_str = textToTranslate,
                        source_lang = lang1,
                        target_lang = lang2,
                        translate_mode = TranslateModeType.SENTENCES,
                    ).translate()['result']

                    self.__languageSwitchText.set(lang1 + " ⥎ " + lang2)
            except:
                # note: modifies deepL status to allow for the next if
                # to run
                self.__toggleDeepStatus()

        if not self.__useDeepL:
            if forceLanguage is None:
                textObject = TextBlob(textToTranslate)
                languageGuess = textObject.detect_language()

                # Note: Defaults to German if unknown
                if languageGuess == "en":
                    result = GoogleTranslator(
                        source = "english",
                        target = "german"
                    ).translate(textToTranslate)
                    self.__languageSwitchText.set("EN" + " ⥎ " + "DE")
                else:
                    result = GoogleTranslator(
                        source = 'german',
                        target = 'english'
                    ).translate(textToTranslate)
                    self.__languageSwitchText.set("DE" + " ⥎ " + "EN")
            else:
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
                self.__languageSwitchText.set(lang1 + " ⥎ " + lang2)


        self.__originalTextFrame.updateText(textToTranslate)
        self.__translatedTextFrame.updateText(result)

    def getCurrentText(self):
        return self.__originalTextFrame.getText()

    class TextFrame(Frame):
        def __init__(self, root, lockEntry = True):
            super().__init__(root, borderwidth = 0, highlightthickness = 0)
            super().pack_propagate(False)
            self.__isLocked = lockEntry
            self.__text = Text(
                self,
                height = 100,
                font = ("Times New Roman", 12),
                wrap = WORD
            )
            self.__text.insert(END, "")
            self.__text.pack(anchor = W, fill = BOTH, side = BOTTOM)
            self.__text.configure(state = DISABLED if lockEntry else NORMAL)

        def updateText(self, updatedText):
            self.__text.configure(state = NORMAL)
            self.__text.delete("1.0", END)
            self.__text.insert(END, updatedText)
            self.__text.configure(
                state = DISABLED if self.__isLocked else NORMAL)

        def getText(self):
            return self.__text.get("1.0",'end-1c')

        def updateHeaderText(self, text):
            self.__languageHeaderText.set(text)

        def bindText(self, key, binding):
            self.__text.bind(key, binding)