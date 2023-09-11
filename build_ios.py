import os 

os.system("pyinstaller " +
"-F  --onefile --noconsole --icon=logosmall.ico " +
"--windowed " +
"--add-data=gefplus/static/*.png;static " + 
"main.py")
