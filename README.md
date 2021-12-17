# German-Pocketbook
A simple graphical user interface to connect both dictionary functionalities and general translator functions. The former pulls from dict.cc ([fork source](https://github.com/rbaron/dict.cc.py)), and the latter takes from Google Translate and DeepL when possible. Note that these use unofficial scraping means to attain information, and the dependencies are (as a result) prone to failure.

<img src="/github_images/dictionary.png" width="450">
<img src="/github_images/translator.png" width="450">

Only (at the moment) works between English and German.

Supports CLI arguments.

## Shortcuts:
### Global:
F1 or Control+1: Switch to dictionary tab

F2 or Control+2: Switch to Translator tab

### Translator:
F5: Switch both language and text.

F6: Switch language.

F7: Switch text.

F12: Toggle DeepL usage.

## Notes:
### Required Libraries
pydeeplator

deep_translator

### License
Public Domain
