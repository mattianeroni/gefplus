import os 

os.system("pyinstaller " +
"-F  --onefile --noconsole --icon=logosmall.ico " +
"--add-data=gefplus/static/*.png;static " + 
"main.py")