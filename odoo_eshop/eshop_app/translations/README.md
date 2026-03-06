To Manage translation
=====================

Generate template '.pot' file (each time)
-----------------------------------------
It will update pot with new line numbers, new fields

```
cd ./odoo_eshop/eshop_app

../../env/bin/pybabel extract -F translations/settings_babel.cfg -o translations/i18n.pot .
```

Generate '.po' files (First Time)
---------------------------------
pybabel init -i translations/i18n.pot -d translations -l fr


Generate '.po' files (Next times)
---------------------------------

```
../../env/bin/pybabel update -i translations/i18n.pot -d translations
```

Translate all strings in messages.po
------------------------------------
Some strings are marked as fuzzy (Babel tried to translated automatically), change translation if needed and remove "#fuzzy" line


Generate '.mo' file
-------------------
../../env/bin/pybabel compile -d translations


Relaunch application
-------------------