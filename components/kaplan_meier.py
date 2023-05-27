import PySimpleGUI as sg
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt 
from sksurv.nonparametric import kaplan_meier_estimator
from PIL import Image 


def draw_figure(canvas, figure):
    """ Draw figure into Canvas """
    #if canvas: canvas.get_tk_widget().pack_forget()  # remove previous image
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=False)
    return figure_canvas_agg




class KaplanMeier:

    code = "-KAPLAN_MEIER"

    layout = [
        [sg.Canvas(size=(40, 40), key='-KAPLAN_MEIER-')],
        [   
            sg.Text("Survival days:",), sg.Combo([], size=(20,4), enable_events=True, key='-KAPLAN_MEIER_X-'), 
            sg.Text("Information presence:"), sg.Combo([], size=(20,4), enable_events=True, key='-KAPLAN_MEIER_Y-'),
            #sg.Button("Update", enable_events=True, key="-UPDATE_KAPLAN_MEIER-")
        ],
        [
            sg.Text("Filter:"), sg.Combo([], size=(20,4), enable_events=True, key='-KAPLAN_MEIER_FILTER-'),
        ],
        [sg.FileSaveAs("Save", enable_events=True, key="-SAVE_KAPLAN_MEIER-", file_types=(('PNG', '*.png'),))]
    ]


    def __init__ (self, window, df):
        """ 
        Initialise the component.

        :param window: The window where the component is drawn
        :param df: The dataframe of the main data table
        """
        # Update fields used for graphs computation
        options = df.columns.values.tolist()
        window["-KAPLAN_MEIER_X-"].update(value=options[0], values=options)
        window["-KAPLAN_MEIER_Y-"].update(value=options[1], values=options)
        
        # Remember the data source and the currently considered data
        self.window = window
        self.df = df 
        self.death_registered = df[options[0]]
        self.survival_time = df[options[1]]

        # Compute curve and update the figure 
        self.compute_curve()


    def compute_curve (self):
        """ Compute the Kaplan Meier curve """
        try:
            time, survival_prob = kaplan_meier_estimator(self.death_registered, self.survival_time)
        except Exception as e:
            time, survival_prob = tuple(), tuple()
            
        # Plot and save the figure
        fig, ax = plt.subplots()
        ax.step(time, survival_prob, where="post")
        ax.set_ylabel("Probability of survival")
        ax.set_xlabel("Time")

        self.canvas = draw_figure(self.window['-KAPLAN_MEIER-'].TKCanvas, fig)
        self.figure = fig 


    def trigger (self, event, values):
        """ Check if the current event trigger something in the component """

        # Update x and y axis of curve
        if event == "-KAPLAN_MEIER_X-" or event == "-KAPLAN_MEIER_Y-":
            df = self.df
            self.canvas.get_tk_widget().forget()
            self.death_registered = df[values["-KAPLAN_MEIER_Y-"]]
            self.survival_time = df[values["-KAPLAN_MEIER_X-"]]
            self.compute_curve()

        # Save the plot
        elif event == "-SAVE_KAPLAN_MEIER-":
            plt.figure(self.figure.number)
            plt.savefig(values["-SAVE_KAPLAN_MEIER-"])