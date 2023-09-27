import tkinter as tk
import tkinter.messagebox
from tkinter import filedialog, ttk, Scale

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from parameter import Parameters
from SCR_Response import SCR_RESP
class FearDisplayApp:
    def __init__(self):
        self.max_us = 0
        self.CSP_df = None
        self.CSP_res_figure = None
        self.CSP_response = 0
        self.CSM_df = None
        self.CSM_res_figure = None
        self.CSM_response = 0
        self.df = None
        self.file_path = ""
        self.min_y_ax1_ax2 = 2.0
        self.max_y_ax1_ax2 = 8.0
        self.min_y_ax3 = -1.0
        self.max_y_ax3 = 1.0
        self.TIME_STEP = 0.1
        self.init_objects()
        self.init_parameters()
        self.init_ui()
    def init_objects(self):

        """
        Initialize objects
        :object parameter:
        -----------------------------------------------------------------------------------------------------------------------------
        :method reset_to_defaults:
        Reset all parameters to their default values.
        :method update_parameters:
        Update parameters with new values
        ------------------------------------------------------------------------------------------------------------------------------
        :object SCR_resp:
        :method SCR_resp:
        :param rise_begin: the minimum response onset time
        :param rise_end:   the maximum response onset time
        :param max_rise_time:  the maximum time of the rising portion
        :param cs_type: CS+, CS-, CS+E
        :param target: which CS to be analyzed (reversed count)
        :param display_window: window (sec)
        :param order: how  to calculate the response target
        :param time_step: time step (sec)
        :method get_SCR_response
        :return : SCR_response
        :method get_SCR_res_figure
        :return: SCR_res_figure
        :method SCR_df:
        :return: SCR_df
        ---------------------------------------------------------------------------------------------------------------------------

        """
        self.parameter = Parameters()
        self.SCR_resp = None

    def init_parameters(self):
        self.rise_begin = self.parameter.rise_begin
        self.rise_end = self.parameter.rise_end
        self.max_rise_time = self.parameter.max_rise_time
        self.display_window = self.parameter.display_window
        self.target = self.parameter.target

    def init_ui(self):
        self.window = tk.Tk()
        self.window.title('Fear Display')
        self.window.geometry('800x600')
        self.window.configure(background='white')

        self.top_frame = tk.Frame(self.window, bg='white')
        self.top_frame.pack(fill=tk.BOTH)

        self.data_btn = tk.Button(self.top_frame, text='Import Data (*.txt)', command=self.open_file)
        self.data_btn.pack(fill=tk.BOTH, expand=True)

        self.param_btn = tk.Button(self.top_frame, text='Parameter Adjustment', command=self.adjust_parameters)
        self.param_btn.pack(fill=tk.BOTH, expand=True)

        self.max_analysis_var = tk.IntVar()
        self.max_analysis_checkbox = ttk.Checkbutton(self.top_frame, text="Standardize", variable=self.max_analysis_var,
                                                     command=self.update_analysis)
        self.max_analysis_checkbox.pack(side=tk.LEFT)

        self.label_frame = tk.Frame(self.window, bg='white')
        self.label_frame.pack(fill=tk.BOTH, expand=True)

        self.csp_label = tk.Label(self.label_frame, text="CS+ Response:", font=("Times New Roman", 10), bg='white')
        self.csp_label.grid(row=1, column=1, padx=30, pady=10)

        self.csm_label = tk.Label(self.label_frame, text="CS- Response:", font=("Times New Roman", 10), bg='white')
        self.csm_label.grid(row=1, column=2, padx=30, pady=10)

        self.mus_label = tk.Label(self.label_frame, text="Max US:", font=("Times New Roman", 10), bg='white')
        self.mus_label.grid(row=1, column=3, padx=30, pady=10)

        self.diff_label = tk.Label(self.label_frame, text="Difference:", font=("Times New Roman", 10), bg='white')
        self.diff_label.grid(row=1, column=4, padx=30, pady=10)

        self.reward_label = tk.Label(self.label_frame, text="Reward: ", font=("Times New Roman", 10), bg='white')
        self.reward_label.grid(row=1, column=5, padx=30, pady=10)

        self.middle_frame = tk.Frame(self.window, bg='white')
        self.middle_frame.pack(fill=tk.BOTH, expand=True)

        self.scale_frame = tk.Frame(self.window)
        self.scale_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)

        self.y_scale_value_ax1 = tk.DoubleVar(value=0)
        self.y_scale_ax1 = Scale(self.scale_frame, from_=0, to=5, resolution=0.01, orient="horizontal",
                                 variable=self.y_scale_value_ax1, command=self.update_plot, length=350)
        self.y_scale_ax1.pack(side=tk.LEFT, padx=10)

        self.y_scale_value_ax3 = tk.DoubleVar(value=0)
        self.y_scale_ax3 = Scale(self.scale_frame, from_=0, to=5, resolution=0.01, orient="horizontal",
                                 variable=self.y_scale_value_ax3, command=self.update_plot, length=350)
        self.y_scale_ax3.pack(side=tk.RIGHT, padx=10)

        self.figure = plt.figure(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.middle_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.ax1 = self.figure.add_subplot(121)
        self.ax3 = self.figure.add_subplot(122)
        self.ax1.set_ylim(self.min_y_ax1_ax2, self.max_y_ax1_ax2)
        self.ax3.set_ylim(self.min_y_ax3, self.max_y_ax3)
    def run(self):
        self.window.mainloop()
    def open_file(self):
        self.file_path = filedialog.askopenfilename(initialdir="/", title="Choose Data",
                                               filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
        if self.file_path:
            self.data_analysis(self.file_path)

    # Find Maximum US
    def max_US_resp(self):
        # set rise_end to capture US response
        if self.rise_end <= 9.2:
            self.rise_end = 9.2
        US_len = len(self.df.loc[self.df[2] == 3])
        max_us_list = []
        for self.target in range(1,US_len+1):
            self.SCR_resp.scr_resp(self.rise_begin,self.rise_end,self.max_rise_time,cs_type=3,
                                   target=self.target,display_window=self.display_window,order = "reverse")
            max_us_list.append(self.SCR_resp.get_SCR_response())
        self.target = self.parameter.target
        self.max_us = round(max(max_us_list),4)

    # Update CS shown on the GUI
    def update_GUI(self,CSP_response, CSM_response):
        self.csp_label.config(text=f"CS+ Response:{CSP_response}")
        self.csm_label.config(text=f"CS- Response:{CSM_response}")
        diff = round(CSP_response - CSM_response, 4)
        self.diff_label.config(text=f"Difference:{diff}")
        reward = round(300 - 100 * diff)
        self.reward_label.config(text=f"Reward:{reward}")

    # Graph Update
    def update_plot(self,CSP_df,CSP_res_figure,CSM_df,CSM_res_figure):
        ##draw graph
        self.figure.clear()
        # set the number of graph
        ax1 = self.figure.add_subplot(121)
        ax3 = self.figure.add_subplot(122)
        # set the y-axis
        ax1.set_ylim(self.min_y_ax1_ax2 - self.y_scale_value_ax1.get(),
                     self.max_y_ax1_ax2 + self.y_scale_value_ax1.get())
        ax3.set_ylim(self.min_y_ax3 - self.y_scale_value_ax3.get(), self.max_y_ax3 + self.y_scale_value_ax3.get())
        # plot the graph
        ax1.plot(CSP_df[1], label="CS+")
        ax1.plot(CSP_res_figure[1], "red")
        ax1.plot(CSM_df[1], "green", label="CS-")
        ax1.plot(CSM_res_figure[1], "red")
        """for i in range(len(infl)):
            ax1.scatter(infl[i],CSP_df[1].iloc[infl[i]])
        for i in range(len(infl2)):
            ax1.scatter(infl2[i],CSM_df[1].iloc[infl2[i]])"""
        # set title
        ax1.set_title("CS+ & CS-")
        ax1.legend()
        ax3.plot((CSP_df[1] - CSM_df[1]))
        ax3.set_title("Difference")
        plt.tight_layout()
        self.canvas.draw()
    def CS_resp_update(self, CSP_response, CSM_response, CSP_df, CSM_df, CSP_res_figure, CSM_res_figure):
        # update CS response shown on the GUI
        self.update_GUI(CSP_response, CSM_response)
        # graph SCR response
        if len(CSP_res_figure) != 0:
            CSP_initial = CSP_res_figure.iloc[0].name
            CSP_res_figure.index = range(CSP_df.index.get_loc(CSP_initial) + 1,
                                         CSP_df.index.get_loc(CSP_initial) + len(CSP_res_figure) + 1)
        if len(CSM_res_figure) != 0:
            CSM_initial = CSM_res_figure.iloc[0].name
            CSM_res_figure.index = range(CSM_df.index.get_loc(CSM_initial) + 1,
                                         CSM_df.index.get_loc(CSM_initial) + len(CSM_res_figure) + 1)
        CSP_df.index = range(1, len(CSP_df) + 1)
        CSM_df.index = range(1, len(CSM_df) + 1)
        ##Find y-axis
        self.min_y_ax1_ax2 = min(min(CSP_df[1]), min(CSM_df[1])) - 0.5
        self.max_y_ax1_ax2 = max(max(CSP_df[1]), max(CSM_df[1])) + 0.5
        self.min_y_ax3 = min(CSP_df[1] - CSM_df[1]) - 0.5
        self.max_y_ax3 = max(CSP_df[1] - CSM_df[1]) + 0.5
        self.update_plot(CSP_df, CSP_res_figure, CSM_df, CSM_res_figure)

    def update_analysis(self):
        if self.max_analysis_var.get() == 1:
            #standarize data
            CSP_response = round((self.CSP_response / self.max_us), 4)
            CSM_response = round((self.CSM_response / self.max_us), 4)
            CSP_df = self.CSP_df / self.max_us
            CSM_df = self.CSM_df / self.max_us
            CSP_res_figure = self.CSP_res_figure / self.max_us
            CSM_res_figure = self.CSM_res_figure / self.max_us
            self.CS_resp_update(CSP_response, CSM_response, CSP_df, CSM_df, CSP_res_figure, CSM_res_figure)
        else:
            # before standardized
            self.CS_resp_update(self.CSP_response, self.CSM_response, self.CSP_df, self.CSM_df, self.CSP_res_figure, self.CSM_res_figure)
    # Data analysis
    def data_analysis(self,file_path):
        # load data
        self.df = pd.read_csv(file_path, delimiter="\t", header=None)
        # create SCR_RESP
        self.SCR_resp = SCR_RESP(self.df)
        # CS Response
        ##CS+
        self.SCR_resp.scr_resp(self.rise_begin,self.rise_end,self.max_rise_time,
                                     cs_type=2,target=self.target,display_window=self.display_window,order="reverse")
        self.CSP_response = self.SCR_resp.get_SCR_response()
        self.CSP_df = self.SCR_resp.get_SCR_df()
        self.CSP_res_figure = self.SCR_resp.get_SCR_res_figure()
        ##CS-
        self.SCR_resp.scr_resp(self.rise_begin,self.rise_end,self.max_rise_time,
                                     cs_type=1,target=self.target,display_window=self.display_window,order="reverse")
        self.CSM_response = self.SCR_resp.get_SCR_response()
        self.CSM_df = self.SCR_resp.get_SCR_df()
        self.CSM_res_figure = self.SCR_resp.get_SCR_res_figure()
        # Standardization
        ###US
        self.max_US_resp()
        self.mus_label.config(text=f"Max US:{self.max_us:}")
        ###update and draw CSP and CSM
        self.update_analysis()
        # figure
        ##reset index
        """global infl
        infl = find_inflection(CSP_df)
        print(infl)
        global infl2
        infl2 = find_inflection(CSM_df)
        print("CSP",infl2)"""

    def adjust_parameters(self):
        # ---------------------------- PARAMETER SETTINGS ------------------------------- #
        RISE_BEGIN_DEFAULT = "0.5"
        RISE_END_DEFAULT = "4.5"
        DISPLAY_WINDOW_DEFAULT = "10"
        MAX_RISE_TIME_DEFAULT = "5.0"
        TARGET_DEFAULT = "1"
        # ---------------------------- PARAMETER SETTINGS ------------------------------- #
        param_window = tk.Toplevel(self.window)
        param_window.title("Parameter Adjustment")

        # Adjust window place
        main_window_x = self.window.winfo_x()
        main_window_y = self.window.winfo_y()
        main_window_width = self.window.winfo_width()
        param_window_x = main_window_x + main_window_width + 10
        param_window_y = main_window_y
        # Adjust the size of the window
        param_window.geometry("300x250+{}+{}".format(param_window_x, param_window_y))

        ## Rise time begin and end
        tk.Label(param_window, text="Rise Time Begin").pack()
        rise_begin = tk.Entry(param_window)
        rise_begin.insert(0, RISE_BEGIN_DEFAULT)
        rise_begin.pack()

        tk.Label(param_window, text="Rise Time End").pack()
        rise_end = tk.Entry(param_window)
        rise_end.insert(0, RISE_END_DEFAULT)
        rise_end.pack()
        ## window
        tk.Label(param_window, text="Window").pack()
        display_window = tk.Entry(param_window)
        display_window.insert(0, DISPLAY_WINDOW_DEFAULT)
        display_window.pack()
        ## maximum rise time
        tk.Label(param_window, text="Maximum Rise Time").pack()
        max_rise_time = tk.Entry(param_window)
        max_rise_time.insert(0, MAX_RISE_TIME_DEFAULT)
        max_rise_time.pack()
        ##target
        tk.Label(param_window, text="Target").pack()
        target = tk.Entry(param_window)
        target.insert(0, TARGET_DEFAULT)
        target.pack()

        confirm_btn = tk.Button(param_window, text="Apply", command=lambda : self.apply_parameters(rise_begin.get(), rise_end.get(), display_window.get(), max_rise_time.get(), target.get()))
        confirm_btn.pack()
    def apply_parameters(self,rise_begin, rise_end, display_window, max_rise_time, target):
        """
        Apply the given parameters to the data analysis.

        Args:
            rise_begin (str): The beginning of the rise period.
            rise_end (str): The end of the rise period.
            display_window (str): The window size for displaying the data.
            max_rise_time (str): The maximum rise time allowed.
            target (str): The target value for analysis.

        Returns:
            None
        """
        # validate input parameters
        try:
            self.rise_begin = float(rise_begin)
            self.rise_end = float(rise_end)
            self.display_window = float(display_window)
            self.max_rise_time = float(max_rise_time)
            self.target = int(target)
        except ValueError:
            tk.messagebox.showerror("Invalid Value", "Error, please type valid value.")

        # check if target is valid
        if (self.target <= 0) or (self.target >= len(self.df[self.df[2] == 2]) + 1):
            tk.messagebox.showerror("Invalid Value", "Error, please type valid value.")

        # Re-plot
        self.data_analysis(self.file_path)

if __name__ == "__main__":
    app = FearDisplayApp()
    app.run()

