To Manage translation
=====================

Generate template '.pot' file (each time)
-----------------------------------------
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

Generate '.mo' file
-------------------
../../env/bin/pybabel compile -d translations
