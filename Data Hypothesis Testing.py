#import package
from scipy import stats
import pandas as pd
import os
class hypothesis_testing:
    #initialize
    def __init__(self):
        pass
    def data_loading(self,filepath,test_start = 0):
        data = pd.read_excel(filepath, index_col=0)
        data.dropna(axis=0, inplace=True)
        if len(data["difference"]) >test_start:
            return(data["difference"].iloc[test_start:])
        else:
            return(data["difference"])
    def hypothesis_testing(self,data,mean=0,alpha=0.05):
        t_stat, p_value = stats.ttest_1samp(data, mean)
        print("t-statistic:", t_stat)
        print("p-value:", p_value)
        if p_value < alpha:
            print("Reject the null hypothesis: The mean is not equal to 0.")
        else:
            print("Fail to reject the null hypothesis: The mean is equal to 0.")

    def batch_testing(self,folderpath,mean=0,alpha=0.05,test_start=0):
        for filename in os.listdir(folderpath):
            filepath = os.path.join(folderpath, filename)
            data = self.data_loading(filepath,test_start)
            print(filename)
            self.hypothesis_testing(data,mean,alpha)

if __name__ == '__main__':
    h = hypothesis_testing()
    """
    h.hypothesis_testing(h.data_loading(r"D:\data\Day2\result\excel_data\reinst_group_ledalab.csv.xlsx"))
    """
    #day1
    h.batch_testing(r"D:\data\Day1\leda\result\excel_data",mean=0,alpha=0.05)
    #day2
    h.batch_testing(r"D:\data\Day2\result\excel_data",mean=0,alpha=0.05)

