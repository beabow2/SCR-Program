# import pakages
import pandas as pd
import os


class Ledalab_Cleaning():

    # initialize
    def __init__(self):
        # CS-
        self.CSM = None
        self.CSM_reext = None
        self.CSM_reinst = None
        # CS+
        self.CSP = None
        self.CSP_reext = None
        self.CSP_reinst = None
        # reext
        self.reext = None
        # reinst
        self.reinst = None

    # def data_loading function
    def data_loading(self, file_path, delimiter="\t"):
        # only load txt file
        if os.path.exists(file_path) and file_path.endswith(".txt"):
            df = pd.read_csv(file_path, delimiter=delimiter)
            return df

    def event_separate(self, data):
        # find CS- response
        self.CSM = data[data["Event.NID"] == 1]["CDA.PhasicMax"]
        # find CS+ response
        self.CSP = data[data["Event.NID"] == 2]["CDA.PhasicMax"]
    def phase_separate(self, ext_num):
        event_list = ["CSM", "CSP"]
        for event in event_list:
            df = getattr(self, event)
            df.name = event
            # reext
            # find corresponding df
            df_reext = df.iloc[:ext_num]
            # reindex
            df_reext.index = range(1, len(df_reext) + 1)
            # reinst
            df_reinst = df.iloc[-ext_num:]
            df_reinst.index = range(1, len(df_reinst) + 1)
            # assign value
            setattr(self, f'{event}_reext', df_reext)
            setattr(self, f'{event}_reinst', df_reinst)

    def combine_event(self):
        # reext
        self.reext = pd.concat([self.CSM_reext, self.CSP_reinst], axis=1)
        # reinst
        self.reinst = pd.concat([self.CSM_reinst, self.CSP_reinst], axis=1)

    def reext_output(self, filename,save_path):
        csv_file_name = f"reext_{filename[:-17]}_ledalab.csv"
        self.reext.to_csv(save_path+csv_file_name, index=True)

    def reinst_output(self, filename,save_path):
        csv_file_name = f"reinst_{filename[:-17]}_ledalab.csv"
        self.reinst.to_csv(save_path+csv_file_name, index=True)

    # batch data cleaning
    def ledalab_cleaning(self, filename, ext_num):
            loaded_data = self.data_loading(filename)
            # separate event
            self.event_separate(loaded_data)
            # separate phase
            self.phase_separate(ext_num)
            # combine event
            self.combine_event()


    def day2_data_output(self,folder_path,save_path,ext_num):
        #create reext and reinst group
        total_reext_df = {'CSM': [0] * 100, 'CSP': [0] * 100,'difference': [0] * 100}
        total_reext_df = pd.DataFrame.from_dict(total_reext_df)
        # reset index
        total_reext_df.index = range(1, len(total_reext_df) + 1)
        total_reinst_df = {'CSM': [0] * 100, 'CSP': [0] * 100,'difference': [0] * 100}
        total_reinst_df = pd.DataFrame.from_dict(total_reinst_df)
        #reset index
        total_reinst_df.index = range(1, len(total_reinst_df) + 1)
        #clean all data
        file_counter = 0
        for filename in os.listdir(folder_path):
            # Data loading
            file_path = os.path.join(folder_path, filename)
            if not file_path.endswith('.txt'):
                continue
            self.ledalab_cleaning(file_path,ext_num)
            #cal difference
            self.reext['difference'] = round(self.reext['CSP'] - self.reext['CSM'],4)
            self.reinst['difference'] = round(self.reinst['CSP'] - self.reinst['CSM'],4)
            # output individual analysis to CSV
            self.reext_output(filename,save_path)
            self.reinst_output(filename,save_path)
            #add group analysis
            total_reext_df += self.reext
            total_reinst_df += self.reinst
            file_counter += 1

        # Save group analysis
        csv_file_name = f"reext_group_{filename[:-17]}_ledalab.csv"
        total_reext_df = round(total_reext_df/file_counter,4)
        total_reext_df.to_csv(save_path+csv_file_name, index=True)
        csv_file_name = f"reinst_group_{filename[:-17]}_ledalab.csv"
        total_reinst_df = round(total_reinst_df/file_counter,4)
        total_reinst_df.to_csv(save_path+csv_file_name, index=True)

app = Ledalab_Cleaning()
app.day2_data_output(r"D:\data\ledalab\Day2\clean",r"D:\data\ledalab\Day2\clean\result\\",15)
