import tkinter as tk
from tkinter import filedialog, ttk, Scale
import tkinter.messagebox

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from scipy.signal import find_peaks

# ---------------------------- CONSTANTS ------------------------------- #
DEFAULT_RISE_BEGIN = 0.5
DEFAULT_RISE_END = 4.5
DEFAULT_DISPLAY_WINDOW = 10.0
DEFAULT_MAX_RISE_TIME = 5.0
DEFAULT_TARGET = 1

# Define Default Parameter
rise_begin = DEFAULT_RISE_BEGIN
rise_end = DEFAULT_RISE_END
display_window = DEFAULT_DISPLAY_WINDOW
max_rise_time = DEFAULT_MAX_RISE_TIME
target = DEFAULT_TARGET

# main program
# Find inflection point
"""def find_inflection(data):
    inflection_points = list()
    diff_data = np.diff(data[1])
    diff2_data = np.diff(data[1],n=2)
    diff3_data = np.diff(data[1],n=3)
    for i in range(0, len(data[1]) - 3):
        if (diff2_data[i] < 0+10**(-5)) & (diff2_data[i] > 0-10**(-5)):
            if  (diff3_data[i] > 0) &(diff_data[i+1] < 0.005):
                inflection_points.append(i+2)
    return(inflection_points)"""


# Define SCR Response
def SCR_resp(rise_begin, rise_end, max_rise_time, situation, target, display_window):
    # initialize min and max index
    max_index = 0
    min_index = 0
    place_SCR = df.loc[df[2] == situation].iloc[-target][0]
    # Estimate CS Response
    # SCR_start = df[(df[0] >= place_SCR + rise_begin) & (df[0] <= place_SCR + rise_end)]
    # SCR_window = df[(df[0]>= place_SCR + rise_begin) & (df[0]<= place_SCR+display_window-rise_begin)]
    ## find the space of scr response
    SCR_start = df[(df[0] >= place_SCR + rise_begin) & (df[0] <= place_SCR + rise_end)]
    SCR_df = df[(df[0] >= place_SCR) & (df[0] <= place_SCR + display_window)]
    trough_index = find_peaks(-SCR_start[1])[0]
    SCR_response = 0
    ## if there is not trougt found in the space
    if len(trough_index) == 0:
        SCR_response = 0
        min_index = 0
        max_index = 0
        # if we ignore rise_begin
        if rise_begin == 0:
            min_index = SCR_start[1].idxmin()
            if (min_index + int(max_rise_time / 0.1)) <= SCR_df.iloc[-1].name:
                SCR_peaks = SCR_df.loc[min_index:min_index + int(max_rise_time / 0.1)]
            else:
                SCR_peaks = SCR_df.loc[min_index:]
            peak_index = find_peaks(SCR_peaks[1])[0]
            SCR_min = SCR_peaks[1].iloc[0]
            # if no peak
            if len(peak_index) == 0:
                SCR_response = 0
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
            SCR_peaks = SCR_df[trough_index[i] + int(rise_begin / 0.1):trough_index[i] + int(rise_begin / 0.1) + int(
                max_rise_time / 0.1) + 1]
            peak_index = find_peaks(SCR_peaks[1])[0]
            SCR_troughrow = SCR_peaks.iloc[0]
            SCR_min = SCR_troughrow[1]
            min_index_temp = SCR_troughrow.name
            # if no peak
            if len(peak_index) == 0:
                SCR_response = 0
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
                    min_index = min_index_temp
    # draw the response
    SCR_res_figure = SCR_df.loc[min_index:max_index]
    trough_check = find_peaks(-SCR_res_figure[1])[0]
    # if there is trough between the response
    if len(trough_check) != 0:
        SCR_response = 0
        min_index = 0
        max_index = 0
        SCR_res_figure = SCR_df.loc[min_index:max_index]
    return (SCR_response, SCR_df, SCR_res_figure)


# Graph Update
def update_plot(event=None):
    ##draw graph
    figure.clear()
    # set the number of graph
    ax1 = figure.add_subplot(121)
    ax3 = figure.add_subplot(122)
    # set the y-axis
    ax1.set_ylim(min_y_ax1_ax2 - y_scale_value_ax1.get(), max_y_ax1_ax2 + y_scale_value_ax1.get())
    ax3.set_ylim(min_y_ax3 - y_scale_value_ax3.get(), max_y_ax3 + y_scale_value_ax3.get())
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
    canvas.draw()


# Find Maximum US
def max_US_resp(rise_begin, rise_end, max_rise_time, target, display_window):
    # set rise_end to capture US response
    if rise_end <= 9.2:
        rise_end = 9.2
    US_len = len(df.loc[df[2] == 3])
    max_us = 0
    # find maximum US response
    max_us_list = [SCR_resp(rise_begin, rise_end, max_rise_time, 3, target, display_window)[0] for target in
                   range(1, US_len + 1)]
    max_us_temp = max(max_us_list)
    if max_us_temp > max_us and max_us_list != 0:
        max_us = max_us_temp
    return (max_us)


# Update CS Response
def CS_resp_update(CSP_res_temp, CSM_res_temp, CSP_df_temp, CSM_df_temp, CSP_res_figure_temp, CSM_res_figure_temp):
    global CSP_response
    global CSM_response
    global CSP_df
    global CSM_df
    global CSP_res_figure
    global CSM_res_figure
    # update CS response
    CSP_response = CSP_res_temp
    CSM_response = CSM_res_temp
    CSP_df = CSP_df_temp
    CSM_df = CSM_df_temp
    CSP_res_figure = CSP_res_figure_temp
    CSM_res_figure = CSM_res_figure_temp
    # update CS response shown on the GUI
    CSP_label.config(text=f"CS+ Response:{CSP_response:}")
    CSM_label.config(text=f"CS- Response:{CSM_response:}")
    diff = round(CSP_response - CSM_response, 4)
    Diff_label.config(text=f"Difference:{diff}")
    reward = round(300 - 100 * diff)
    reward_label.config(text=f"Reward:{reward:}")
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
    global min_y_ax1_ax2
    global max_y_ax1_ax2
    min_y_ax1_ax2 = min(min(CSP_df[1]), min(CSM_df[1])) - 0.5
    max_y_ax1_ax2 = max(max(CSP_df[1]), max(CSM_df[1])) + 0.5
    global min_y_ax3
    global max_y_ax3
    min_y_ax3 = min(CSP_df[1] - CSM_df[1]) - 0.5
    max_y_ax3 = max(CSP_df[1] - CSM_df[1]) + 0.5


# Data analysis
def data_analysis(file_path, rise_begin, rise_end, display_window, max_rise_time, target):
    global CSP_response_ns
    global CSM_response_ns
    global CSP_df_ns
    global CSM_df_ns
    global CSP_res_figure_ns
    global CSM_res_figure_ns
    global CSP_response_stand
    global CSM_response_stand
    global CSP_df_stand
    global CSM_df_stand
    global CSP_res_figure_stand
    global CSM_res_figure_stand
    global df
    # load data
    df = pd.read_csv(file_path, delimiter="\t", header=None)
    # CS Response
    ##CS+
    CSP_fun = SCR_resp(rise_begin, rise_end, max_rise_time, 2, target, display_window)
    CSP_response_ns = round(CSP_fun[0], 4)
    CSP_df_ns = CSP_fun[1]
    CSP_res_figure_ns = CSP_fun[2]
    ##CS-
    CSM_fun = SCR_resp(rise_begin, rise_end, max_rise_time, 1, target, display_window)
    CSM_response_ns = round(CSM_fun[0], 4)
    CSM_df_ns = CSM_fun[1]
    CSM_res_figure_ns = CSM_fun[2]
    # Standardization
    ###US
    max_us = round(max_US_resp(rise_begin, rise_end, max_rise_time, target, display_window), 4)
    MUS_label.config(text=f"Max US:{max_us:}")
    ###Standarize CSP and CSM
    CSP_response_stand = round(CSP_response_ns / max_us, 4)
    CSM_response_stand = round(CSM_response_ns / max_us, 4)
    CSP_df_stand = CSP_df_ns / max_us
    CSM_df_stand = CSM_df_ns / max_us
    CSP_res_figure_stand = CSP_res_figure_ns / max_us
    CSM_res_figure_stand = CSM_res_figure_ns / max_us
    if max_analysis_var.get() == 1:
        CS_resp_update(CSP_response_stand, CSM_response_stand, CSP_df_stand, CSM_df_stand, CSP_res_figure_stand,
                       CSM_res_figure_stand)
    else:
        CS_resp_update(CSP_response_ns, CSM_response_ns, CSP_df_ns, CSM_df_ns, CSP_res_figure_ns, CSM_res_figure_ns)
    # figure
    ##reset index
    """global infl
    infl = find_inflection(CSP_df)
    print(infl)
    global infl2
    infl2 = find_inflection(CSM_df)
    print("CSP",infl2)"""
    # draw graph
    update_plot()


# ---------------------------- PARAMETER SETTINGS ------------------------------- #
def adjust_parameters():
    param_window = tk.Toplevel(window)
    param_window.title("Parameter Adjustment")

    # Adjust window place
    main_window_x = window.winfo_x()
    main_window_y = window.winfo_y()
    main_window_width = window.winfo_width()
    param_window_x = main_window_x + main_window_width + 10
    param_window_y = main_window_y
    # Adjust the size of the window
    param_window.geometry("300x250+{}+{}".format(param_window_x, param_window_y))

    ## Rise time begin and end
    tk.Label(param_window, text="Rise Time Begin").pack()
    rise_begin = tk.Entry(param_window)
    rise_begin.insert(0, "0.5")
    rise_begin.pack()

    tk.Label(param_window, text="Rise Time End").pack()
    rise_end = tk.Entry(param_window)
    rise_end.insert(0, "4.5")
    rise_end.pack()
    ## window
    tk.Label(param_window, text="Window").pack()
    display_window = tk.Entry(param_window)
    display_window.insert(0, "10")
    display_window.pack()
    ## maximum rise time
    tk.Label(param_window, text="Maximum Rise Time").pack()
    max_rise_time = tk.Entry(param_window)
    max_rise_time.insert(0, "5.0")
    max_rise_time.pack()
    ##target
    tk.Label(param_window, text="Target").pack()
    target = tk.Entry(param_window)
    target.insert(0, "1")
    target.pack()

    confirm_btn = tk.Button(param_window, text="Apply",
                            command=lambda: apply_parameters(rise_begin.get(), rise_end.get(),
                                                             display_window.get(), max_rise_time.get(), target.get()))
    confirm_btn.pack()


def apply_parameters(rise_begin, rise_end, display_window, max_rise_time, target):
    try:
        # update parameter
        rise_begin = float(rise_begin)
        rise_end = float(rise_end)
        display_window = float(display_window)
        max_rise_time = float(max_rise_time)
        target = int(target)
        if (target <= 0) or (target >= len(df[df[2] == 2]) + 1):
            ## error
            tk.messagebox.showerror("Invalid Value", "Error, please type valid value.")
        else:
            # Re-plot
            data_analysis(file_path, rise_begin, rise_end, display_window, max_rise_time, target)
    except ValueError:
        tk.messagebox.showerror("Invalid Value", "Error, please type valid value.")


# Standardize checkbox
def toggle_analysis():
    if max_analysis_var.get() == 1:
        # after standardized
        CS_resp_update(CSP_response_stand, CSM_response_stand, CSP_df_stand, CSM_df_stand, CSP_res_figure_stand,
                       CSM_res_figure_stand)
        update_plot()
    else:
        # before standardized
        CS_resp_update(CSP_response_ns, CSM_response_ns, CSP_df_ns, CSM_df_ns, CSP_res_figure_ns, CSM_res_figure_ns)
        update_plot()


# ---------------------------- LOAD FILE ------------------------------- #
def open_file():
    global file_path
    file_path = filedialog.askopenfilename(initialdir="/", title="Choose Data",
                                           filetypes=(("txt files", "*.txt"), ("all files", "*.*")))
    if file_path:
        data_analysis(file_path, rise_begin, rise_end, display_window, max_rise_time, target)


# ---------------------------- UI SETUP ------------------------------- #
window = tk.Tk()
window.title('Fear Display')
window.geometry('800x600')
window.configure(background='white')

# Create Button
top_frame = tk.Frame(window, bg='white')
top_frame.pack(fill=tk.BOTH)

data_btn = tk.Button(top_frame, text='Import Data (*.txt)', command=open_file)
data_btn.pack(fill=tk.BOTH, expand=True)

param_btn = tk.Button(top_frame, text='Parameter Adjustment', command=adjust_parameters)
param_btn.pack(fill=tk.BOTH, expand=True)

# Create a button to trigger analysis
max_analysis_var = tk.IntVar()
max_analysis_checkbox = ttk.Checkbutton(top_frame, text="Standardize", variable=max_analysis_var,
                                        command=toggle_analysis)
max_analysis_checkbox.pack(side=tk.LEFT)

# Create a frame to hold the labels
label_frame = tk.Frame(window, bg='white')
label_frame.pack(fill=tk.BOTH, expand=True)

# CS+
CSP_label = tk.Label(label_frame, text="CS+ Response:", font=("Times New Roman", 10), bg='white')
CSP_label.grid(row=1, column=1, padx=30, pady=10)

# CS-
CSM_label = tk.Label(label_frame, text="CS- Response:", font=("Times New Roman", 10), bg='white')
CSM_label.grid(row=1, column=2, padx=30, pady=10)

# Max US
MUS_label = tk.Label(label_frame, text="Max US:", font=("Times New Roman", 10), bg='white')
MUS_label.grid(row=1, column=3, padx=30, pady=10)

# Difference
Diff_label = tk.Label(label_frame, text="Difference:", font=("Times New Roman", 10), bg='white')
Diff_label.grid(row=1, column=4, padx=30, pady=10)

# Reward
reward_label = tk.Label(label_frame, text="Reward: ", font=("Times New Roman", 10), bg='white')
reward_label.grid(row=1, column=5, padx=30, pady=10)

# Create Canvas
middle_frame = tk.Frame(window, bg='white')
middle_frame.pack(fill=tk.BOTH, expand=True)

# create Bar
scale_frame = tk.Frame(window)
scale_frame.pack(side=tk.BOTTOM, fill=tk.BOTH)

y_scale_value_ax1 = tk.DoubleVar(value=0)
y_scale_ax1 = Scale(scale_frame, from_=0, to=5, resolution=0.01, orient="horizontal", variable=y_scale_value_ax1,
                    command=update_plot, length=350)
y_scale_ax1.pack(side=tk.LEFT, padx=10)

y_scale_value_ax3 = tk.DoubleVar(value=0)
y_scale_ax3 = Scale(scale_frame, from_=0, to=5, resolution=0.01, orient="horizontal", variable=y_scale_value_ax3,
                    command=update_plot, length=350)
y_scale_ax3.pack(side=tk.RIGHT, padx=10)

# Default Canvas
figure = plt.figure(figsize=(10, 6))
canvas = FigureCanvasTkAgg(figure, master=middle_frame)
canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
ax1 = figure.add_subplot(121)
ax3 = figure.add_subplot(122)
ax1.set_ylim(2.0, 8.0)
ax3.set_ylim(-1.0, 1.0)
window.mainloop()
