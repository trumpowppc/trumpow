Translation Strings Policy
===========================

This document provides guidelines for internationalization of the Trumpow Core software.

How to translate?
------------------

To mark a message as translatable

- In GUI source code (under `src/qt`): use `tr("...")`

- In non-GUI source code (under `src`): use `_("...")`

No internationalization is used for e.g. developer scripts outside `src`.

Strings to be translated
-------------------------

On a high level, these strings are to be translated:

- GUI strings, anything that appears in a dialog or window

- Command-line option documentation

### GUI strings

Anything that appears to the user in the GUI is to be translated. This includes labels, menu items, button texts, tooltips and window titles.
This includes messages passed to the GUI through the UI interface through `InitMessage`, `ThreadSafeMessageBox` or `ShowProgress`.

### Command-line options

Documentation for the command line options in the output of `--help` should be translated as well.

Make sure that default values do not end up in the string, but use string formatting like `strprintf(_("Threshold for disconnecting misbehaving peers (default: %u)"), 100)`. Putting default values in strings has led to accidental translations in the past, and forces the string to be re-translated every time the value changes.

Do not translate messages that are only shown to developers, such as those that only appear when `--help-debug` is used.

General recommendations
------------------------

### Avoid unnecessary translation strings

Try not to burden translators with translating messages that are e.g. slight variations of other messages.
In the GUI, avoid the use of text where an icon or symbol will do.
Make sure that placeholder texts in forms don't end up in the list of strings to be translated (use `<string notr="true">`).

### Make translated strings understandable

Try to write translation strings in an understandable way, for both the user and the translator. Avoid overly technical or detailed messages

### Do not translate internal errors

Do not translate internal errors, or log messages, or messages that appear on the RPC interface. If an error is to be shown to the user,
use a translatable generic message, then log the detailed message to the log. E.g. "A fatal internal error occurred, see debug.log for details".
This helps troubleshooting; if the error is the same for everyone, the likelihood is increased that it can be found using a search engine.

### Avoid fragments

Avoid dividing up a message into fragments. Translators see every string separately, so may misunderstand the context if the messages are not self-contained.

### Avoid HTML in translation strings

There have been difficulties with use of HTML in translation strings; translators should not be able to accidentally affect the formatting of messages.
This may sometimes be at conflict with the recommendation in the previous section.

### Plurals

Plurals can be complex in some languages. A quote from the gettext documentation:

    In Polish we use e.g. plik (file) this way:
    1 plik,
    2,3,4 pliki,
    5-21 pliko'w,
    22-24 pliki,
    25-31 pliko'w
    and so on

In Qt code use tr's third argument for optional plurality. For example:

    tr("%n hour(s)","",secs/HOUR_IN_SECONDS);
    tr("%n day(s)","",secs/DAY_IN_SECONDS);
    tr("%n week(s)","",secs/WEEK_IN_SECONDS);

This adds `<numerusform>`s to the respective `.ts` file, which can be translated separately depending on the language. In English, this is simply:

    <message numerus="yes">
        <source>%n active connection(s) to Bitcoin network</source>
        <translation>
            <numerusform>%n active connection to Bitcoin network</numerusform>
            <numerusform>%n active connections to Bitcoin network</numerusform>
        </translation>
    </message>

Where it is possible try to avoid embedding numbers into the flow of the string at all. e.g.

    WARNING: check your network connection, %d blocks received in the last %d hours (%d expected)

versus

    WARNING: check your network connection, less blocks (%d) were received in the last %n hours than expected (%d).

The second example reduces the number of pluralized words that translators have to handle from three to one, at no cost to comprehensibility of the sentence.

### Finding strings to translate

Translation files are in the directory `src/qt/locale/` and have the `.ts` suffix.

If you have the `lupdate` Qt development tool installed, run `make translate language=...` from the `src/` directory.
This will update translation files in the locale directory. For the `language` argument, use a language suffix and
optional country code. For example, `make translate language=en_GB` will update the English language (`en`) file for
the United Kingdom (`GB`). Look at the translation files for examples of existing supported languages

In the appropriate file for your language/locale, look for entries with the tags `type="unfinished"`. These are new, untranslated entries.
When you finish translating them, remove that tag.

You may also see entries with the tag `type="vanished"`. These are entries where the original text has been removed from the source code.
Remove these in a separate step.

### String freezes

During a string freeze (often before a major release), no translation strings are to be added, modified or removed.

This can be checked by executing `make translate` in the `src` directory, then verifying that `bitcoin_en.ts` remains unchanged.
