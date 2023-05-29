import PySimpleGUI as sg
import pingouin as pg



class Anova:

    code = "-ANOVA-"


    layout = [
        [
            sg.Table(
                values=[], 
                headings=["Source", "SS", "DF", "MS", "F", "p-unc", "np2"], 
                auto_size_columns=False, 
                enable_events=True, 
                col_widths=20,
                justification='center',
                key="-ANOVA_TABLE-",
            )
        ],
        [    
            sg.Text("Affected:"), sg.Combo([], size=(20,4), enable_events=True, key='-ANOVA_Y-'),
        ],
        [sg.Text("Factors:")],
        [sg.Text("         "), sg.Listbox([], size=(20, 5), select_mode='extended', enable_events=True,  key='-ANOVA_FACTORS-')],
        [sg.FileSaveAs("Save", enable_events=True, key="-SAVE_ANOVA-", file_types=(('CSV', '*.csv'),))]
    ]


    def __init__(self, window, df):
        self.window = window 
        self.df = df
        self.headers = ("Source", "SS", "DF", "MS", "F", "p-unc", "np2")

        fields = df.columns.values.tolist()
        window["-ANOVA_FACTORS-"].update(fields)
        window["-ANOVA_Y-"].update(value=fields[0], values=fields)

        try:
            self.result_table = pg.anova(data=self.df, dv=values["-ANOVA_Y-"], between=values["-ANOVA_FACTORS-"], detailed=True).values.tolist()
        except:
            self.result_table = []



    def trigger (self, event, values):
        if event == "-ANOVA_Y-" or event == "-ANOVA_FACTORS-":
            try:
                self.result_table = pg.anova(data=self.df, dv=values["-ANOVA_Y-"], between=values["-ANOVA_FACTORS-"], detailed=True).values.tolist()
            except Exception as ex:
                self.result_table = []

            self.window["-ANOVA_TABLE-"].update(self.result_table)

        # Save the anova table
        elif event == "-SAVE_ANOVA-":
            df = pd.DataFrame(self.result_table, columns=self.headers)
            df.to_csv(values["-SAVE_ANOVA-"])