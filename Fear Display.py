import tkinter as tk
import tkinter.messagebox
from tkinter import filedialog, ttk, Scale

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import find_peaks
from parameter import Parameters
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
        self.TIME_STEP = 0.5
        self.parameter = Parameters()
        self.init_ui()

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

        self.window.mainloop()
    def run(self):
        self.window.mainloop()
    def open_file(self):
        self.file_path = filedialog.askopenfilename(initialdir="/", title="Choose Data",
                                               filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
        if self.file_path:
            self.data_analysis(self.file_path, self.parameter.rise_begin, self.parameter.rise_end, self.parameter.display_window,
                          self.parameter.max_rise_time, self.parameter.target)

    def SCR_resp(self,rise_begin, rise_end, max_rise_time, situation, target, display_window, time_step=0.5):
        """
        :param rise_begin: the minimum response onset time
        :param rise_end:   the maximum response onset time
        :param max_rise_time:  the maximum time of the rising portion
        :param situation: CS+, CS-, CS+E
        :param target: which CS to be analyzed (reversed count)
        :param display_window: window (sec)
        :param time_step: time step (sec)
        :return:
        """
        min_index = 0
        max_index = 0
        place_SCR = self.df.loc[self.df[2] == situation].iloc[-target][0]  # event onset time
        print(place_SCR)

        # Estimate CS Response
        SCR_start = self.df[(self.df[0] >= place_SCR + rise_begin) & (self.df[0] <= place_SCR + rise_end)]
        SCR_df = self.df[(self.df[0] >= place_SCR) & (self.df[0] <= place_SCR + display_window)]
        trough_index = find_peaks(-SCR_start[1])[0]
        SCR_response = 0
        # if no trough found in the space
        if len(trough_index) == 0:
            min_index = 0
            max_index = 0

            # if we ignore rise_begin
            if rise_begin == 0:
                min_index = SCR_start[1].idxmin()
                if (min_index + int(max_rise_time / time_step)) <= SCR_df.iloc[-1].name:
                    SCR_peaks = SCR_df.loc[min_index:min_index + int(max_rise_time / time_step)]
                else:
                    SCR_peaks = SCR_df.loc[min_index:]
                peak_index = find_peaks(SCR_peaks[1])[0]
                SCR_min = SCR_peaks[1].iloc[0]

                # if no peak
                if len(peak_index) == 0:
                    min_index = 0
                    max_index = 0
                # if peak
                else:
                    SCR_peakrow = SCR_peaks.iloc[peak_index[0]]
                    SCR_max = SCR_peakrow[1]
                    SCR_response_temp = SCR_max - SCR_min
                    if SCR_response_temp > SCR_response:
                        SCR_response = SCR_response_temp
                        max_index = SCR_peakrow.name
        # if we find trough in the space
        else:
            for i in range(len(trough_index)):
                SCR_peaks = SCR_df[trough_index[i] + int(rise_begin / time_step):trough_index[i] + int(
                    rise_begin / time_step) + int(
                    max_rise_time / time_step) + 1]
                print("SCR_peaks",SCR_peaks)
                peak_index = find_peaks(SCR_peaks[1])[0]
                SCR_troughrow = SCR_peaks.iloc[0]
                SCR_min = SCR_troughrow[1]
                min_index_temp = SCR_troughrow.name

                # if no peak
                if len(peak_index) == 0:
                    min_index = 0
                    max_index = 0
                # if peak
                else:
                    SCR_peakrow = SCR_peaks.iloc[peak_index[0]]
                    SCR_max = SCR_peakrow[1]
                    SCR_response_temp = SCR_max - SCR_min
                    print("SCR_max:",SCR_max,"SCR_min:", SCR_min)
                    if SCR_response_temp > SCR_response:
                        SCR_response = SCR_response_temp
                        max_index = SCR_peakrow.name
                        min_index = min_index_temp

        # draw the response
        SCR_res_figure = SCR_df.loc[min_index:max_index]
        trough_check = find_peaks(-SCR_res_figure[1])[0]
        print(min_index)
        print(max_index)
        # if there is trough between the response
        if len(trough_check) != 0:
            SCR_response = 0
            min_index = 0
            max_index = 0
            SCR_res_figure = SCR_df.loc[min_index:max_index]

        if situation == 1:
            self.CSM_df = SCR_df
            self.CSM_res_figure = SCR_res_figure
            self.CSM_response = SCR_response
        elif situation == 2 :
            self.CSP_df = SCR_df
            self.CSP_res_figure = SCR_res_figure
            self.CSP_response = SCR_response


        return SCR_response

    # Find Maximum US
    def max_US_resp(self,rise_begin, rise_end, max_rise_time, display_window):
        # set rise_end to capture US response
        if rise_end <= 9.2:
            rise_end = 9.2
        US_len = len(self.df.loc[self.df[2] == 3])
        max_us_list = [self.SCR_resp(rise_begin, rise_end, max_rise_time, 3, target, display_window) for target in
                       range(1, US_len + 1)]
        self.max_us = max(max_us_list)
        print(self.max_us)

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
    def data_analysis(self,file_path, rise_begin, rise_end, display_window, max_rise_time, target):
        # load data
        self.df = pd.read_csv(file_path, delimiter="\t", header=None)
        # CS Response
        ##CS+
        self.SCR_resp(rise_begin, rise_end, max_rise_time, 2, target, display_window)
        ##CS-
        self.SCR_resp(rise_begin, rise_end, max_rise_time, 1, target, display_window)
        # Standardization
        ###US
        self.max_US_resp(rise_begin, rise_end, max_rise_time, display_window)
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
        # draw graph
        self.update_plot(self.CSP_df, self.CSP_res_figure, self.CSM_df, self.CSM_res_figure)


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
            rise_begin = float(rise_begin)
            rise_end = float(rise_end)
            display_window = float(display_window)
            max_rise_time = float(max_rise_time)
            target = int(target)
        except ValueError:
            tk.messagebox.showerror("Invalid Value", "Error, please type valid value.")

        # check if target is valid
        if (target <= 0) or (target >= len(self.df[self.df[2] == 2]) + 1):
            tk.messagebox.showerror("Invalid Value", "Error, please type valid value.")

        # Re-plot
        self.data_analysis(self.file_path, rise_begin, rise_end, display_window, max_rise_time, target)

app = FearDisplayApp()
app.run()

