import PySimpleGUI as sg


def new():
    return [
        [
            sg.Column([[sg.Text("Welcome to GEF+!")]]),
            sg.VSeparator(),
            sg.Column([[
                sg.FileBrowse("Import", file_types=[("*.csv", "*.txt",)], 
                enable_events=True, key="-BROWSER-")]]),
        ],
        [
            sg.Table(
                values=[[" "]*10 for _ in range(25)], 
                headings=[f"Column{i}" for i in range(10)], 
                auto_size_columns=True, 
                enable_events=True, 
                size=(40, 20),
                key="-PREVIEW-",
                justification='center',
            )
        ],
        [
            sg.Text("_"*110),
        ],
        [
            sg.TabGroup(
                [[
                    sg.Tab("Anova", [], key='-ANOVA-'),

                ]], 
                key='-TAB_GROUP-'
            ),
        ],
    ]
