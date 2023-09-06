import os 
os.system("pyinstaller" +
" -F  --onefile --noconsole --icon=logosmall.ico" +
" --add-data=gefplus/static/import.png;. " + 
" --add-data=gefplus/static/export.png;. " + 
" --add-data=gefplus/static/autofill.png;. " + 
" --add-data=gefplus/static/logo.jpeg;. " + 
" --add-data=gefplus/static/logosmall.png;. " + 
" --add-data=gefplus/static/settings.png;. " + 
"main.py")