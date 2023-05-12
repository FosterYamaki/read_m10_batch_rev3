#!/usr/bin/env python
# coding: utf-8

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import math
import glob


class M10_Processing : 
    def __init__(self, file_path) : 
        self.file_path = file_path
        print("create 'M10 Processing' class")
        print(f"file path : {self.file_path}")

    def normalizing(self, freq, data, target=100) : 
        idx_1khz = np.where(freq.values == target)[0][0]
        norm = data - data.iloc[idx_1khz, :]
        return norm


    def read_m10(self) : 
        # m10_file_path = "/content/drive/MyDrive/Colab Notebooks/read_m10/M10/m10_sample.M10"
        m10_file_path = self.file_path

        self.output_dir = m10_file_path.split("/")[:-2]
        self.output_dir = "/".join(self.output_dir)
        if "\\" in m10_file_path : 
            self.output_name = m10_file_path.split("\\")[-1]
        else : 
            self.output_name = m10_file_path.split("/")[-1]
        self.output_name = self.output_name.split(".")[0]
        print(self.output_name)

        col_names = [i for i in range(11)]
        data = pd.read_csv(m10_file_path, names=col_names, header=None)
        # key = data.iloc[109, :][0]
        # key = data.iloc[100, :][0]
        # key = "FREQ,SPL,IMP,PHS,SPL1,SPL2,THD,2ND,3RD,SPL30,SPL60"
        # print(data[0])
        for i, line in enumerate(data[0]) : 
            if "FREQ" in line : 
                print(i)
        # print(key)
        # start_idx = np.where(data[0].values == key)[0]
        start_idx = [i for i, line in enumerate(data[0]) if "FREQ" in line] 
        # print(start_idx)
        ts_idx = [i for i, line in enumerate(data[0]) if "MEATIME" in line] 
        # print(ts_idx)

        data_len = 529

        self.time_list = []

        data_dict = {}
        for i, idx in enumerate(start_idx) : 
            print(idx)
            col_name = data.iloc[idx, :].copy()
            time_stamp_line = data.iloc[ts_idx[i], :][0]
            time_stamp = time_stamp_line.split("=")[1]
            self.time_list.append(f"{time_stamp}_data{str(i+1).zfill(4)}")
            data_pick = data.iloc[idx+1:idx+(data_len+1), :].reset_index(drop=True)
            data_pick.columns = col_name
            if i == 0 : 
                array_freq = np.array(data_pick["FREQ"].copy().astype(float))
                array_spl = np.array(data_pick["SPL"].copy().astype(float))
                p0 = 10 ** (np.array(data_pick["SPL"].copy().astype(float)) / 20) 
                array_imp = np.array(data_pick["IMP"].copy().astype(float))
                array_thd = np.array(data_pick["THD"].copy().astype(float))
                hd = 10 ** (np.array(data_pick["THD"].copy().astype(float)) / 20) 
                pthd = np.array(hd / p0 * 100)
                array_pthd = np.array(pthd)
                #array_hd2 = np.array(data_pick["2ND"].copy().astype(float))
                #array_hd3 = np.array(data_pick["3RD"].copy().astype(float))
            else : 
                array_freq = np.concatenate([array_freq, np.array(data_pick["FREQ"].copy().astype(float))])
                array_spl = np.concatenate([array_spl, np.array(data_pick["SPL"].copy().astype(float))])
                p0 = 10 ** (np.array(data_pick["SPL"].copy().astype(float)) / 20) 
                array_imp = np.concatenate([array_imp, np.array(data_pick["IMP"].copy().astype(float))])
                array_thd = np.concatenate([array_thd, np.array(data_pick["THD"].copy().astype(float))])
                hd = 10 ** (np.array(data_pick["THD"].copy().astype(float)) / 20) 
                pthd = np.array(hd / p0 * 100)
                array_pthd = np.concatenate([array_pthd, pthd])
                #array_hd2 = np.concatenate([array_hd2, np.array(data_pick["2ND"].copy().astype(float))])
                #array_hd3 = np.concatenate([array_hd3, np.array(data_pick["3RD"].copy().astype(float))])
            
            if i%100 == 0 : 
                print(f"{i} / {len(start_idx)}")
        self.df_freq = pd.DataFrame(array_freq.reshape((-1, data_len)).T)
        self.df_spl = pd.DataFrame(array_spl.reshape((-1, data_len)).T)
        self.df_imp = pd.DataFrame(array_imp.reshape((-1, data_len)).T)
        self.df_thd = pd.DataFrame(array_thd.reshape((-1, data_len)).T)
        self.df_pthd = pd.DataFrame(array_pthd.reshape((-1, data_len)).T)
        #self.df_hd2 = pd.DataFrame(array_hd2.reshape((-1, data_len)).T)
        #self.df_hd3 = pd.DataFrame(array_hd3.reshape((-1, data_len)).T)

        self.df_freq.columns = self.time_list
        self.df_spl.columns = self.time_list
        self.df_imp.columns = self.time_list
        self.df_thd.columns = self.time_list
        self.df_pthd.columns = self.time_list
        #self.df_hd2.columns = self.time_list
        #self.df_hd3.columns = self.time_list



        self.df_norm = self.normalizing(freq=self.df_freq.iloc[:, 0], data=self.df_spl)
        print("Done")


    def write_excel(self, output_dir) : 

        out_cols = ["Freq"] + self.time_list
        freq = self.df_freq.iloc[:, 0]
        spl_df_out = pd.concat([freq, self.df_spl], axis=1)
        imp_df_out = pd.concat([freq, self.df_imp], axis=1)
      #  thd_df_out = pd.concat([freq, self.df_thd], axis=1)
        pthd_df_out = pd.concat([freq, self.df_pthd], axis=1)
       # hd2_df_out = pd.concat([freq, self.df_hd2], axis=1)
       # hd3_df_out = pd.concat([freq, self.df_hd3], axis=1)

        spl_df_out.columns = out_cols
        imp_df_out.columns = out_cols
      #  thd_df_out.columns = out_cols
        pthd_df_out.columns = out_cols
      #  hd2_df_out.columns = out_cols
      #  hd3_df_out.columns = out_cols

        # name = "test"

        with pd.ExcelWriter(f"{output_dir}/{self.output_name}.xlsx") as writer:
            spl_df_out.to_excel(writer, index=False, sheet_name="SPL_dB") 
            imp_df_out.to_excel(writer, index=False, sheet_name="IMP_ohm")
          #  thd_df_out.to_excel(writer, index=False, sheet_name="THD_dB")    
            pthd_df_out.to_excel(writer, index=False, sheet_name="THD_%")     
          #  hd2_df_out.to_excel(writer, index=False, sheet_name="HD2_dB")
          #  hd3_df_out.to_excel(writer, index=False, sheet_name="HD3_dB")

        print("write excel, Done ")



def m10_batch(folder_path, output_dir) : 
    file_path_list = glob.glob(f"{folder_path}/*.M10")

    for file_path in file_path_list : 
        test = M10_Processing(file_path=file_path)
        test.read_m10()
        test.write_excel(output_dir=output_dir)


