import tkinter as tk
from tkinter import ttk, filedialog, messagebox, Scale

import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from SCRAnalysis import SCRAnalysis

class SCRGUI:
    def __init__(self, scr_analysis):
        self.scr_analysis = scr_analysis
        self.window = tk.Tk()
        self.window.title('Fear Display')
        self.window.geometry('800x600')
        self.window.configure(background='white')
        self.file_path = None
        self.ax3 = None
        self.ax1 = None
        self.canvas = None
        self.figure = None
        self.y_scale_ax3 = None
        self.y_scale_value_ax3 = None
        self.y_scale_ax1 = None
        self.y_scale_value_ax1 = None
        self.reward_label = None
        self.scale_frame = None
        self.middle_frame = None
        self.diff_label = None
        self.mus_label = None
        self.csm_label = None
        self.csp_label = None
        self.label_frame = None
        self.max_analysis_checkbox = None
        self.max_analysis_var = None
        self.param_btn = None
        self.data_btn = None
        self.top_frame = None
        self.init_ui()

    def init_ui(self):
        # Initialize UI components
        # Create Button
        self.top_frame = tk.Frame(self.window, bg='white')
        self.top_frame.pack(fill=tk.BOTH)

        self.data_btn = tk.Button(self.top_frame, text='Import Data (*.txt)', command=self.open_file)
        self.data_btn.pack(fill=tk.BOTH, expand=True)

        self.param_btn = tk.Button(self.top_frame, text='Parameter Adjustment', command=self.adjust_parameters)
        self.param_btn.pack(fill=tk.BOTH, expand=True)

        self.max_analysis_var = tk.IntVar()
        self.max_analysis_checkbox = ttk.Checkbutton(self.top_frame, text="Standardize", variable=self.max_analysis_var,
                                                     command=self.scr_analysis.toggle_analysis)
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
        # Default Canvas
        self.figure = plt.figure(figsize=(10, 6))
        self.canvas = FigureCanvasTkAgg(self.figure, master=self.middle_frame)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.ax1 = self.figure.add_subplot(121)
        self.ax3 = self.figure.add_subplot(122)
        self.ax1.set_ylim(2.0, 8.0)
        self.ax3.set_ylim(-1.0, 1.0)

    def open_file(self):
        self.file_path = filedialog.askopenfilename(
            initialdir="/", title="Choose Data",
            filetypes=(("txt files", "*.txt"), ("all files", "*.*"))
        )
        if self.file_path:
            self.scr_analysis.load_data(self.file_path)
            # More code to update UI
            self.scr_analysis.data_analysis(self.file_path, self.scr_analysis.parameters.rise_begin,
                                            self.scr_analysis.parameters.rise_end,
                                            self.scr_analysis.parameters.display_window,
                                            self.scr_analysis.parameters.max_rise_time,
                                            self.scr_analysis.parameters.target)

    def adjust_parameters(self):
        self.param_window = tk.Toplevel(self.window)
        self.param_window.title("Parameter Adjustment")

        # Adjust window place
        self.main_window_x = self.window.winfo_x()
        self.main_window_y = self.window.winfo_y()
        self.main_window_width = self.window.winfo_width()
        self.param_window_x = self.main_window_x + self.main_window_width + 10
        self.param_window_y = self.main_window_y
        # Adjust the size of the window
        self.param_window.geometry("300x250+{}+{}".format(self.param_window_x, self.param_window_y))

        ## Rise time begin and end
        tk.Label(self.param_window, text="Rise Time Begin").pack()
        self.rise_begin = tk.Entry(self.param_window)
        self.rise_begin.insert(0, "0.5")
        self.rise_begin.pack()

        tk.Label(self.param_window, text="Rise Time End").pack()
        self.rise_end = tk.Entry(self.param_window)
        self.rise_end.insert(0, "4.5")
        self.rise_end.pack()
        ## window
        tk.Label(self.param_window, text="Window").pack()
        self.display_window = tk.Entry(self.param_window)
        self.display_window.insert(0, "10")
        self.display_window.pack()
        ## maximum rise time
        tk.Label(self.param_window, text="Maximum Rise Time").pack()
        self.max_rise_time = tk.Entry(self.param_window)
        self.max_rise_time.insert(0, "5.0")
        self.max_rise_time.pack()
        ##target
        tk.Label(self.param_window, text="Target").pack()
        self.target = tk.Entry(self.param_window)
        self.target.insert(0, "1")
        self.target.pack()

        self.confirm_btn = tk.Button(self.param_window, text="Apply",
                                     command=lambda: self.apply_parameters(self.rise_begin.get(), self.rise_end.get(),
                                                                           self.display_window.get(),
                                                                           self.max_rise_time.get(),
                                                                           self.target.get()))
        self.confirm_btn.pack()

    #
    def apply_parameters(self):
        # Read the values from the UI and update the parameters
        try:
            self.scr_analysis.parameters.update_parameters(
                rise_begin=float(self.rise_begin.get()),
                rise_end=float(self.rise_end.get()),
                display_window=float(self.display_window.get()),
                max_rise_time=float(self.max_rise_time.get()),
                target=int(self.target.get())
            )
            if (self.scr_analysis.parameters.target <= 0) \
                    or (self.scr_analysis.parameters.target >=
                        len(self.scr_analysis.df[self.scr_analysis.df[2] == 2]) + 1):
                # error
                messagebox.showerror("Invalid Value", "Error, please type valid value.")
            else:
                # Re-plot
                self.update_plot()
        except ValueError:
            messagebox.showerror("Invalid Value", "Error, please type valid value.")
        # Re-plot or update the analysis


    def update_plot(self):
        self.scr_analysis.data_analysis()
        # Your update_plot code here
        # draw graph
        self.figure.clear()

        # set the y-axis
        self.ax1.set_ylim(min_y_ax1_ax2 - y_scale_value_ax1.get(), max_y_ax1_ax2 + y_scale_value_ax1.get())
        self.ax3.set_ylim(min_y_ax3 - y_scale_value_ax3.get(), max_y_ax3 + y_scale_value_ax3.get())
        # plot the graph
        self.ax1.plot(CSP_df[1], label="CS+")
        self.ax1.plot(CSP_res_figure[1], "red")
        self.ax1.plot(CSM_df[1], "green", label="CS-")
        self.ax1.plot(CSM_res_figure[1], "red")
        """for i in range(len(infl)):
            ax1.scatter(infl[i],CSP_df[1].iloc[infl[i]])
        for i in range(len(infl2)):
            ax1.scatter(infl2[i],CSM_df[1].iloc[infl2[i]])"""
        # set title
        self.ax1.set_title("CS+ & CS-")
        self.ax1.legend()
        self.ax3.plot((CSP_df[1] - CSM_df[1]))
        self.ax3.set_title("Difference")
        plt.tight_layout()
        self.canvas.draw()

    def run(self):
        self.window.mainloop()
