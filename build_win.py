import os 

os.system("pyinstaller " +
"-F  --onefile --noconsole --icon=logosmall.ico " +
"--name GEF+ " + 
"--add-data=gefplus/static/*.png;static " + 
"main.py")
