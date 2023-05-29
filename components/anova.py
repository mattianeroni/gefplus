

class Anova:

    code = "-ANOVA-"


    layout = [
        [sg.Canvas(size=(40, 40), key='-KAPLAN_MEIER-')],
        [   
            sg.Text("Survival days:",), sg.Combo([], size=(20,4), enable_events=True, key='-KAPLAN_MEIER_X-'), 
            sg.Text("Information presence:"), sg.Combo([], size=(20,4), enable_events=True, key='-KAPLAN_MEIER_Y-'),
        ],
        
        [sg.FileSaveAs("Save", enable_events=True, key="-SAVE_ANOVA-", file_types=(('CSV', '*.csv'),))]
    ]