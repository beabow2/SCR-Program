from parameter import Parameters
from SCRGUI import SCRGUI
from SCRAnalysis import SCRAnalysis

if __name__ == "__main__":
    parameters = Parameters()
    scr_analysis = SCRAnalysis(parameters)
    scr_gui = SCRGUI(scr_analysis)
    scr_gui.run()
