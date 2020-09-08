import tkinter as tk
import threading
import subprocess
import signal
import json
import getpass
import glob
import os
import hashlib
import logging
import unittest
import test_psl_file_content
import test_file_name_format
import test_datafiles
import test_chk01_intensive_checklist
import test_msl_file_content
import test_tsl_file_content
import test_chk01_checklist
import test_epsig_log_files
import test_chk01_checklist_game_removals
import webbrowser
import atexit
import time

from datetime import datetime
from tkinter import *
from tkinter import ttk
from tkinter import filedialog, messagebox

from test_datafiles import QCASTestClient, PSLfile, PSLEntry_OneHash, TSLfile, MSLfile, Preferences, skipping_PSL_comparison_tests

VERSION = "0.2"
DF_DIRECTORY = "G:/OLGR-TECHSERV/MISC/BINIMAGE/qcas/"
os.system('mode con: cols=150 lines=120')

logging.basicConfig(level=logging.DEBUG,
        format='%(asctime)s - %(levelname)-8s %(message)s',
        datefmt='%d-%m-%y %H:%M',
        filename='qcas_test.log',
        filemode='a')
        
class qcas_df_gui: 

    # Constructor
    def __init__(self):
        self.my_preferences = Preferences() 
        self.root = tk.Tk()       
        self.config_fname = "preferences.dat"
        self.my_unittests = list()
        self.my_test_output = list()
        self.proc = None
        
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        optionmenu = tk.Menu(menubar, tearoff=0)

        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Exit", command=self.root.destroy)
        
        menubar.add_cascade(label="Help", menu=optionmenu)
        optionmenu.add_command(label="About this Program", command=None)
        optionmenu.add_command(label="How To Use", command=self.howToUse)

        self.root.config(menu=menubar)
        threading.Thread(self.setUpGUI()).start()        

    def howToUse(self): 
        url = 'https://github.com/icarus523/qcasDFtest/blob/master/README.md'
        webbrowser.open_new(url)
            
        
    ############# GUI Related ################## 
    def setUpGUI(self):
        self.root.wm_title("qcasDF GUI Control v" + VERSION)        
        
        self.root.resizable(1,1)    
        self.root.focus_force()  
        self.tf_current_msl = None
        self.tf_nextmonth_msl = None
        ######## Top Frame
        frame_toparea = ttk.Labelframe(self.root, text="Location of QCAS Data Files: ")
        frame_toparea.pack(side = TOP, fill=X, expand=False)
        frame_toparea.config(relief = RIDGE, borderwidth = 1)
        
        ######## Current Month MSL
        frame_current_month_msl = ttk.Frame(frame_toparea)
        frame_current_month_msl.config(relief = FLAT, borderwidth = 1)
        frame_current_month_msl.pack(side = TOP, padx  = 0, pady = 0, expand = False, fill=X, anchor = 'w')       
                                     
        # Button MSL file
        button_select_current_msl = ttk.Button(frame_current_month_msl, text = "MSL File...", width=20, 
            command = lambda: self.handleButtonPress('__select_current_msl_file__'))                                             
        button_select_current_msl.pack(side=LEFT, padx = 3, pady = 3, fill=X, expand=False)        
        # Text Entry Current MSL file
        v_msl = StringVar() 
        self.tf_current_msl = ttk.Entry(frame_current_month_msl, width = 100, textvariable = v_msl)
        v_msl.set(self.my_preferences.data['MSLfile'])
        self.tf_current_msl.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)

        ######## Next Month MSL
        frame_next_month_msl = ttk.Frame(frame_toparea)
        frame_next_month_msl.config(relief = FLAT, borderwidth = 1)
        frame_next_month_msl.pack(side = TOP, padx  = 0, pady = 0, expand = False, fill=X, anchor = 'w')       

        # Button Next Month MSL file
        self.button_select_nextmonth_msl = ttk.Button(frame_next_month_msl, text = "Next Month MSL File...", width=20, 
            command = lambda: self.handleButtonPress('__select_nextmonth_msl_file__'))                                             
        self.button_select_nextmonth_msl.pack(side=LEFT, padx = 3, pady = 3, fill=X, expand=False)        
        # Text Entry Current MSL file
        v = StringVar() 
        self.tf_nextmonth_msl = ttk.Entry(frame_next_month_msl, width = 100, textvariable = v)
        v.set(self.my_preferences.data['nextMonth_MSLfile'])
        self.tf_nextmonth_msl.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)

        ######## Current PSL
        frame_current_psl = ttk.Frame(frame_toparea)
        frame_current_psl.config(relief = FLAT, borderwidth = 1)
        frame_current_psl.pack(side = TOP, padx  = 0, pady = 0, expand = False, fill=X, anchor = 'w')       

        # Button Current PSL file
        button_select_current_psl = ttk.Button(frame_current_psl, text = "PSL File...", width=20, 
            command = lambda: self.handleButtonPress('__select_psl_file__'))                                             
        button_select_current_psl.pack(side=LEFT, padx = 3, pady = 3, fill=X, expand=False)        
        # Text Entry Current PSL file
        v_psl = StringVar() 
        self.tf_current_psl = ttk.Entry(frame_current_psl, width = 100, textvariable = v_psl)
        v_psl.set(self.my_preferences.data['PSLfile'])
        self.tf_current_psl.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)

        ######## Next Month PSL
        frame_next_month_psl = ttk.Frame(frame_toparea)
        frame_next_month_psl.config(relief = FLAT, borderwidth = 1)
        frame_next_month_psl.pack(side = TOP, padx  = 0, pady = 0, expand = False, fill=X, anchor = 'w')       

        # Button Next Month PSL file
        self.button_select_nextmonth_psl = ttk.Button(frame_next_month_psl, text = "Next Month PSL File...", width=20, 
            command = lambda: self.handleButtonPress('__select_nextmonth_psl_file__'))                                             
        self.button_select_nextmonth_psl.pack(side=LEFT, padx = 3, pady = 3, fill=X, expand=False)        
        # Text Next Month PSL file
        v_psl2 = StringVar() 
        self.tf_nextmonth_psl = ttk.Entry(frame_next_month_psl, width = 100, textvariable = v_psl2)        
        v_psl2.set(self.my_preferences.data['nextMonth_PSLfile'])
        self.tf_nextmonth_psl.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)

        ######## Previous Month PSL
        frame_previous_month_psl = ttk.Frame(frame_toparea)
        frame_previous_month_psl.config(relief = FLAT, borderwidth = 1)
        frame_previous_month_psl.pack(side = TOP, padx  = 0, pady = 0, expand = False, fill=X, anchor = 'w')       

        # Button Prev Month PSL file
        self.button_select_prevmonth_psl = ttk.Button(frame_previous_month_psl, text = "Prev. Month PSL File...", width=20, 
            command = lambda: self.handleButtonPress('__select_prevmonth_psl_file__'))                                             
        self.button_select_prevmonth_psl.pack(side=LEFT, padx = 3, pady = 3, fill=X, expand=False)        
        # Text Prev Month PSL file
        v_psl3 = StringVar() 
        self.tf_prevmonth_psl = ttk.Entry(frame_previous_month_psl, width = 100, textvariable = v_psl3)
        v_psl3.set(self.my_preferences.data['previousMonth_PSLfile'])
        self.tf_prevmonth_psl.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)
        
        ######## Current TSL
        frame_current_tsl = ttk.Frame(frame_toparea)
        frame_current_tsl.config(relief = FLAT, borderwidth = 1)
        frame_current_tsl.pack(side = TOP, padx  = 0, pady = 0, expand = False, fill=X, anchor = 'w')       

        # Button Current TSL file
        button_select_current_tsl = ttk.Button(frame_current_tsl, text = "New TSL File...", width=20, 
            command = lambda: self.handleButtonPress('__select_tsl_file__'))                                             
        button_select_current_tsl.pack(side=LEFT, padx = 3, pady = 3, fill=X, expand=False)        
        # Text Entry Current PSL file
        v_tsl = StringVar() 
        self.tf_current_tsl = ttk.Entry(frame_current_tsl, width = 100, textvariable = v_tsl)
        v_tsl.set(self.my_preferences.data['TSLfile'])
        self.tf_current_tsl.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)

        ######## Previous Month TSL
        frame_previous_month_tsl = ttk.Frame(frame_toparea)
        frame_previous_month_tsl.config(relief = FLAT, borderwidth = 1)
        frame_previous_month_tsl.pack(side = TOP, padx  = 0, pady = 0, expand = False, fill=X, anchor = 'w')       

        # Button Previous Month TSL file
        button_select_previousmonth_tsl = ttk.Button(frame_previous_month_tsl, text = "Previous TSL File...", width=20, 
            command = lambda: self.handleButtonPress('__select_previousmonth_tsl_file__'))                                             
        button_select_previousmonth_tsl.pack(side=LEFT, padx = 3, pady = 3, fill=X, expand=False)        
        # Text Previous Month PSL file
        v_tsl2 = StringVar() 
        self.tf_previousmonth_tsl = ttk.Entry(frame_previous_month_tsl, width = 100, textvariable = v_tsl2)
        v_tsl2.set(self.my_preferences.data['previous_TSLfile'])
        self.tf_previousmonth_tsl.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)

        #Frame for Config
        frame_config = ttk.Labelframe(frame_toparea, text="Configuration: ")
        frame_config.pack(side = TOP, fill=BOTH, expand = False)
        frame_config.config(relief = RIDGE, borderwidth = 2)
        
        ######## BINIMAGE Location
        frame_binimage = ttk.Frame(frame_config)
        frame_binimage.config(relief = FLAT, borderwidth = 1)
        frame_binimage.grid(row=1, column=1, sticky='w')

        # Button Binimage Path
        button_binimage_path = ttk.Button(frame_binimage, text = "BINIMAGE PATH...", width=20, 
            command = lambda: self.handleButtonPress('__select_binimage__'))                                             
        button_binimage_path.pack(side=LEFT, padx = 3, pady = 3, expand=True)        
        # Text Binimage Path
        self.v_binimage = StringVar() 
        self.tf_binimage_path= ttk.Entry(frame_binimage, width = 100, textvariable = self.v_binimage)
        self.v_binimage.set(self.my_preferences.data['path_to_binimage'])
        self.tf_binimage_path.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)

        ######## EPSIG Logfile Location
        frame_epsiglog = ttk.Frame(frame_config)
        frame_epsiglog.config(relief = FLAT, borderwidth = 1)
        frame_epsiglog.grid(row=2, column=1, sticky='w')

        # Button Epsig Log Path
        button_epsiglog_path = ttk.Button(frame_epsiglog, text = "epsig Log File...", width=20, 
            command = lambda: self.handleButtonPress('__select_epsiglog_file__'))                                             
        button_epsiglog_path.pack(side=LEFT, padx = 3, pady = 3, fill=X, expand=False)        
        # Text Epsig Log Path
        self.v_epsiglog = StringVar() 
        self.tf_epsiglog_path= ttk.Entry(frame_epsiglog, width = 100, textvariable = self.v_epsiglog)
        self.v_epsiglog.set(self.my_preferences.data['epsig_log_file'])
        self.tf_epsiglog_path.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)

        ######## New Games Text File
        frame_newgames = ttk.Frame(frame_config)
        frame_newgames.config(relief = FLAT, borderwidth = 1)
        frame_newgames.grid(row=3, column=1, sticky='w')

        # Button Epsig Log Path
        button_newgames_path = ttk.Button(frame_newgames, text = "News Games file...", width=20, 
            command = lambda: self.handleButtonPress('__select_newgames__'))                                             
        button_newgames_path.pack(side=LEFT, padx = 3, pady = 3, fill=X, expand=False)        
        # Text Epsig Log Path
        self.v_newgames = StringVar() 
        self.tf_newgames= ttk.Entry(frame_newgames, width = 100, textvariable = self.v_newgames)
        self.v_newgames.set(self.my_preferences.data['write_new_games_to_file'])
        self.tf_newgames.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)        
        
        # Combobox Number of Games to Validate
        frame_combobox = ttk.Frame(frame_config)
        frame_combobox.config(relief = FLAT, borderwidth = 1)
        frame_combobox.grid(row=4, column=1, sticky='w')
        
        self.box_value = IntVar()
        ttk.Label(frame_combobox, justify=LEFT, text = 'Number of Games To Validate: ').pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)
        self.combobox_NumberofGames = ttk.Combobox(frame_combobox, 
            justify=LEFT, 
            textvariable=self.box_value)
        self.combobox_NumberofGames.pack(side=RIGHT, fill=X, padx = 3, pady = 3, expand=True)
        self.combobox_NumberofGames.set(self.my_preferences.data['number_of_random_games']) # default value
        self.combobox_NumberofGames['values'] = ['1', '2', '3', '4', '5', '10', '20']

        # Combobox Acceptable Percentage Change to a PSL file
        frame_combobox_psl_change = ttk.Frame(frame_config)
        frame_combobox_psl_change.config(relief = FLAT, borderwidth = 1)
        frame_combobox_psl_change.grid(row=5, column=1, sticky='w')
        
        self.box_value2 = StringVar()
        ttk.Label(frame_combobox_psl_change, justify=LEFT, text = 'PSL file size changed threshold: ').pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)
        self.combobox_NumberofGames = ttk.Combobox(frame_combobox_psl_change, 
            justify=LEFT, 
            textvariable=self.box_value2)
        self.combobox_NumberofGames.pack(side=RIGHT, fill=X, padx = 3, pady = 3, expand=True)
        def_val = str(self.my_preferences.data['percent_changed_acceptable']*100) + "%"
        self.combobox_NumberofGames.set(def_val) # default value
        self.combobox_NumberofGames['values'] = ['5%','10%', '20%', '30%']
        
        # Checkbutton Intensive Validation
        self.intensive_validation = IntVar()
        if self.my_preferences.data['skip_lengthy_validations'].upper() == "FALSE":
            self.intensive_validation.set(0)
        else:
            self.intensive_validation.set(1)
            
        self.cb_intensive_validation = Checkbutton(
            frame_config, 
            text="Skip Intensive Validations", 
            justify=LEFT, 
            variable = self.intensive_validation, 
            onvalue=1, 
            offvalue=0, 
            command=self.handleCheckButton)
        self.cb_intensive_validation.grid(row=6, column=1, sticky='w')

        # Checkbutton Verbose Mode
        self.verbose_mode = IntVar()
        if self.my_preferences.data['verbose_mode'].upper() == "FALSE":
            self.verbose_mode.set(0)
        else:
            self.verbose_mode.set(1)
            
        self.cb_verbose_mode = Checkbutton(
            frame_config, 
            text="Verbose Mode (Logging)", 
            justify=LEFT, 
            variable = self.verbose_mode, 
            onvalue=1, 
            offvalue=0)
        self.cb_verbose_mode.grid(row=7, column=1, sticky='w')

        # Checkbutton One Month Mode
        self.one_month_mode = IntVar()
        if self.my_preferences.data['one_month_mode'].upper() == "FALSE":
            self.one_month_mode.set(0)
            self.button_select_nextmonth_msl.config(state=NORMAL)
            self.tf_nextmonth_msl.config(state=NORMAL)
            self.button_select_nextmonth_psl.config(state=NORMAL)
            self.tf_nextmonth_psl.config(state=NORMAL)
        else:
            self.one_month_mode.set(1)
            self.button_select_nextmonth_msl.config(state=DISABLED)
            self.tf_nextmonth_msl.config(state=DISABLED)
            self.button_select_nextmonth_psl.config(state=DISABLED)
            self.tf_nextmonth_psl.config(state=DISABLED)
            
        self.cb_one_month_mode = Checkbutton(
            frame_config, 
            text="One Month Mode (Skip PSL comparison validations)", 
            justify=LEFT, 
            variable = self.one_month_mode, 
            onvalue=1, 
            offvalue=0,
            command=self.handleCheckButton)
        self.cb_one_month_mode.grid(row=8, column=1, sticky='w')                
        
        ######## Bottom Frame
        frame_bottomarea = ttk.Frame(self.root)
        frame_bottomarea.pack(side = BOTTOM, fill=X, expand=False)
        frame_bottomarea.config(relief = RIDGE, borderwidth = 1)

        ######## Unittest Frame
        frame_unittest = ttk.Labelframe(frame_bottomarea, text="Unit tests:")
        frame_unittest.pack(side = TOP, fill=X, expand=False)
        frame_unittest.config(relief = RIDGE, borderwidth = 1)
        
        # Checkbutton unit test filename format
        self.unittest_filename_format = IntVar()           
        self.cb_unittest_filename_format = Checkbutton(
            frame_unittest, 
            text="File Name Format", 
            justify=LEFT, 
            variable = self.unittest_filename_format, 
            onvalue=1, 
            offvalue=0,
            command=self.handleCheckButton)
        self.cb_unittest_filename_format.pack(side = LEFT, fill=X, expand=False)
        self.unittest_filename_format.set(1)
        
        # Checkbutton unit test MSL file content
        self.unittest_msl_file_content = IntVar()           
        self.cb_unittest_msl_file_content = Checkbutton(
            frame_unittest, 
            text="MSL file content", 
            justify=LEFT, 
            variable = self.unittest_msl_file_content, 
            onvalue=1, 
            offvalue=0,
            command=self.handleCheckButton)
        self.cb_unittest_msl_file_content.pack(side = LEFT, fill=X, expand=False)
        self.unittest_msl_file_content.set(1)
        
        # Checkbutton unit test PSL file content
        self.unittest_psl_file_content = IntVar()           
        self.cb_unittest_psl_file_content = Checkbutton(
            frame_unittest, 
            text="PSL file content", 
            justify=LEFT, 
            variable = self.unittest_psl_file_content, 
            onvalue=1, 
            offvalue=0,
            command=self.handleCheckButton)
        self.cb_unittest_psl_file_content.pack(side = LEFT, fill=X, expand=False)
        self.unittest_psl_file_content.set(1)
        
        # Checkbutton unit test TSL file content
        self.unittest_tsl_file_content = IntVar()           
        self.cb_unittest_tsl_file_content = Checkbutton(
            frame_unittest, 
            text="TSL file content", 
            justify=LEFT, 
            variable = self.unittest_tsl_file_content, 
            onvalue=1, 
            offvalue=0,
            command=self.handleCheckButton)
        self.cb_unittest_tsl_file_content.pack(side = LEFT, fill=X, expand=False)
        self.unittest_tsl_file_content.set(1)
        
        # Checkbutton unit test epsig log file
        self.unittest_epsig_log_file = IntVar()           
        self.cb_unittest_epsig_log_file = Checkbutton(
            frame_unittest, 
            text="epsig log file", 
            justify=LEFT, 
            variable = self.unittest_epsig_log_file, 
            onvalue=1, 
            offvalue=0,
            command=self.handleCheckButton)
        self.cb_unittest_epsig_log_file.pack(side = LEFT, fill=X, expand=False)
        self.unittest_epsig_log_file.set(1)
        
        # Checkbutton chk01 basic
        self.unittest_chk01_basic = IntVar()           
        self.cb_unittest_chk01_basic = Checkbutton(
            frame_unittest, 
            text="CHK01 Basic", 
            justify=LEFT, 
            variable = self.unittest_chk01_basic, 
            onvalue=1, 
            offvalue=0,
            command=self.handleCheckButton)
        self.cb_unittest_chk01_basic.pack(side = LEFT, fill=X, expand=False)
        self.unittest_chk01_basic.set(1)
        
        # Checkbutton chk01 intensive 
        self.unittest_chk01_intensive = IntVar()           
        self.cb_unittest_chk01_intensive = Checkbutton(
            frame_unittest, 
            text="CHK01 Intensive", 
            justify=LEFT, 
            variable = self.unittest_chk01_intensive, 
            onvalue=1, 
            offvalue=0,
            command=self.handleCheckButton)
        self.cb_unittest_chk01_intensive.pack(side = LEFT, fill=X, expand=False)
        self.unittest_chk01_intensive.set(1)
        self.cb_unittest_chk01_intensive.config(state=DISABLED)
        
        ######## Start Button Frame
        frame_start_button = ttk.Frame(frame_bottomarea)
        frame_start_button.config(relief = FLAT, borderwidth = 1)
        frame_start_button.pack(side = TOP, padx  = 0, pady = 0, expand = False, fill=X, anchor = 'w')       
        # Button Start 
        self.button_start = ttk.Button(frame_start_button, text = "Start Verification", width=20, 
            command = lambda: self.handleButtonPress('__start__'))
        self.button_start.pack(side=RIGHT, padx = 3, pady = 3, fill=X, expand=False)      

        # Button Stop
        button_stop = ttk.Button(frame_start_button, text = "Stop", width=20, 
            command = lambda: self.handleButtonPress('__stop__'))
        button_stop.pack(side=RIGHT, padx = 3, pady = 3, fill=X, expand=False)         
        
        # Button Save Config 
        button_save = ttk.Button(frame_start_button, text = "Save Config", width=20, 
            command = lambda: self.handleButtonPress('__save__'))                 
        button_save.pack(side=LEFT, padx = 3, pady = 3, fill=X, expand=False)       

        self.root.mainloop()

    def handleCheckButton(self): 
        # One Month Mode
        if self.one_month_mode.get() == 1: 
            self.button_select_nextmonth_msl.config(state=DISABLED)
            self.tf_nextmonth_msl.config(state=DISABLED)
            self.button_select_nextmonth_psl.config(state=DISABLED)
            self.tf_nextmonth_psl.config(state=DISABLED)
        else:
            self.button_select_nextmonth_msl.config(state=NORMAL)
            self.tf_nextmonth_msl.config(state=NORMAL)
            self.button_select_nextmonth_psl.config(state=NORMAL)
            self.tf_nextmonth_psl.config(state=NORMAL)
        
        # Build Tests         
        self.my_unittests = list() # clear list    
        self.my_test_output = list() # clear list

        self.my_unittests.append(test_chk01_intensive_checklist)
        self.my_test_output.append("CHK01 Intensive validations")             
        
        # by default always do test_chk01_checklist_game_removals
        self.my_unittests.append(test_chk01_checklist_game_removals)
        self.my_test_output.append("CHK01 game removals")             
            
        if self.unittest_filename_format.get() == 1: 
            self.my_unittests.append(test_file_name_format)
            self.my_test_output.append("Datafile Filename format tests")
            
        if self.unittest_msl_file_content.get() == 1: 
            self.my_unittests.append(test_msl_file_content)
            self.my_test_output.append("MSL File Content Tests: ")
            
        if self.unittest_psl_file_content.get() == 1: 
            self.my_unittests.append(test_psl_file_content)
            self.my_test_output.append("PSL File Content Tests: ")
        
        if self.unittest_tsl_file_content.get() == 1: 
            self.my_unittests.append(test_tsl_file_content)
            self.my_test_output.append("TSL File Content Tests: ")        
        
        if self.unittest_epsig_log_file.get() == 1: 
            self.my_unittests.append(test_epsig_log_files)
            self.my_test_output.append("epsig log file content tests")   

        if self.unittest_chk01_basic.get() == 1: 
            self.my_unittests.append(test_chk01_checklist)
            self.my_test_output.append("CHK01 Validations")           

      
        
    def handleButtonPress(self, choice):
        if choice == '__select_current_msl_file__':
            tmp = filedialog.askopenfilename(initialdir=DF_DIRECTORY, title = "Select Current MSL File",filetypes = (("MSL files","*.MSL"),("all files","*.*")))
            
            if tmp: # Selected something
                self.tf_current_msl.delete(0, END)
                self.tf_current_msl.insert(0, tmp)                
        elif choice == '__select_nextmonth_msl_file__':
            tmp = filedialog.askopenfilename(initialdir=DF_DIRECTORY, title = "Select Next Month MSL File",filetypes = (("MSL files","*.MSL"),("all files","*.*")))
            
            if tmp: # Selected something
                self.tf_nextmonth_msl.delete(0, END)
                self.tf_nextmonth_msl.insert(0, tmp)
        elif choice == '__select_psl_file__':
            tmp = filedialog.askopenfilename(initialdir=DF_DIRECTORY, title = "Select Current PSL File",filetypes = (("PSL files","*.PSL"),("all files","*.*")))
            
            if tmp: # Selected something
                self.tf_current_psl.delete(0, END)                
                self.tf_current_psl.insert(0, tmp)
        elif choice == '__select_nextmonth_psl_file__':
            tmp = filedialog.askopenfilename(initialdir=DF_DIRECTORY, title = "Select Nexth Month PSL File",filetypes = (("PSL files","*.PSL"),("all files","*.*")))
            
            if tmp: # Selected something
                self.tf_nextmonth_psl.delete(0, END)                                
                self.tf_nextmonth_psl.insert(0, tmp)
        elif choice == '__select_prevmonth_psl_file__': 
            tmp = filedialog.askopenfilename(initialdir=DF_DIRECTORY, title = "Select Previous Month PSL File",filetypes = (("PSL files","*.PSL"),("all files","*.*")))
            
            if tmp: # Selected something
                self.tf_prevmonth_psl.delete(0, END)                                
                self.tf_prevmonth_psl.insert(0, tmp)        
        
        elif choice == '__select_tsl_file__':
            tmp = filedialog.askopenfilename(initialdir=DF_DIRECTORY, title = "Select Current TSL File",filetypes = (("TSL files","*.TSL"),("all files","*.*")))
            
            if tmp: # Selected something
                self.tf_current_tsl.delete(0, END)                                                
                self.tf_current_tsl.insert(0, tmp)

        elif choice == '__select_previousmonth_tsl_file__':
            tmp = filedialog.askopenfilename(initialdir=DF_DIRECTORY, title = "Select Previous Month's TSL File",filetypes = (("TSL files","*.TSL"),("all files","*.*")))
            
            if tmp: # Selected something
                self.tf_previousmonth_tsl.delete(0, END)                                
                self.tf_previousmonth_tsl.insert(0, tmp)
                
        elif choice == '__select_binimage__':
            tmp = filedialog.askdirectory(initialdir=self.my_preferences.data['path_to_binimage'], title = "Select BINIMAGE Directory")
            
            if tmp: # Selected something
                self.tf_binimage_path.delete(0, END)                                
                self.tf_binimage_path.insert(0, tmp)

        elif choice == '__select_epsiglog_file__':
            tmp = filedialog.askopenfilename(initialdir=DF_DIRECTORY, title = "Select EPSIG Log file", filetypes = (("TSL files","*.log"),("all files","*.*")))
            
            if tmp: # Selected something
                self.tf_epsiglog_path.delete(0, END)                                
                self.tf_epsiglog_path.insert(0, tmp)
        elif choice == '__select_newgames__':             
            tmp = filedialog.askopenfilename(initialdir='.', title = "Select New Games file",filetypes = (("TXT files","*.TXT"),("all files","*.*")))
            if tmp: # Selected something
                self.tf_newgames.delete(0, END)
                self.tf_newgames.insert(0, tmp)   
            
        elif choice == '__start__':
            self.my_preferences = None 
            self.my_preferences = Preferences() 
            self.handleCheckButton() # get CheckButton unit tests
            self.UpdatePreferences() 

            # 
            command = 'Get-Content -Path qcas_test.log -Wait -Tail 20'
            self.proc_tail = subprocess.Popen(['powershell.exe', command])

            threading.Thread(self.StartUnitTest()).start()                    
            # self.button_start.config(state=DISABLED)         
            self.root.deiconify() # show window  
            
        elif choice == '__save__':
            #self.my_preferences = None 
            # self.my_preferences = Preferences() 
            self.handleCheckButton() # get CheckButton unit tests
            self.UpdatePreferences()
            
        elif choice == '__stop__': 
            if self.proc: 
                self.proc.terminate() # stop process. 
                self.proc = None            
                print("\n### Stopped Validation ###")
                logging.getLogger().info("==== QCAS Unit Test STOPPED/INTERRUPTED: " + str(datetime.now()) + " by: " + getpass.getuser()  + " ====")

            self.button_start.config(state=NORMAL)
            # https://stackoverflow.com/questions/4789837/how-to-terminate-a-python-subprocess-launched-with-shell-true
            # os.killpg(os.getpgid(self.proc_tail.pid), signal.SIGTERM)  # Send the signal to all the process groups
            self.proc_tail.kill()

    def StartUnitTest(self):
        # self.root.withdraw() # hide main window
        self.UpdatePreferences()
        
        if self.proc == None or self.proc.returncode == 0:
            self.proc = subprocess.Popen(['py.exe', '__start_qcas_unittesting_script.py'])
        else: 
            print("\n\n ### Validation in Progress. Please Stop first ###")                
        
    def UpdatePreferences(self):           
        self.my_preferences.data['unittests'] = self.my_test_output
        
        #update vars
        self.my_preferences.data['previous_TSLfile'] = self.tf_previousmonth_tsl.get()
        self.my_preferences.data['TSLfile'] = self.tf_current_tsl.get() 
        self.my_preferences.data['PSLfile'] = self.tf_current_psl.get()
        self.my_preferences.data['nextMonth_PSLfile'] = self.tf_nextmonth_psl.get()
        self.my_preferences.data['previousMonth_PSLfile'] = self.tf_prevmonth_psl.get()        
        self.my_preferences.data['MSLfile'] = self.tf_current_msl.get()
        self.my_preferences.data['nextMonth_MSLfile'] = self.tf_nextmonth_msl.get()
        self.my_preferences.data['number_of_random_games'] = self.box_value.get()
        self.my_preferences.data['epsig_log_file'] = self.v_epsiglog.get()        
        
                      
        if self.intensive_validation.get() == 0: 
            self.my_preferences.data['skip_lengthy_validations'] = "FALSE"
        else:
            self.my_preferences.data['skip_lengthy_validations'] = "TRUE"            

        if self.verbose_mode.get() == 0:
            self.my_preferences.data['verbose_mode'] = "FALSE"
        else:
            self.my_preferences.data['verbose_mode'] = "TRUE"

        if self.box_value2.get() == '5%': 
            self.my_preferences.data['percent_changed_acceptable'] = 0.05
        elif self.box_value2.get() == '10%':
            self.my_preferences.data['percent_changed_acceptable'] = 0.10
        elif self.box_value2.get() == '20%':
            self.my_preferences.data['percent_changed_acceptable'] = 0.20
        elif self.box_value2.get() == '30%':
            self.my_preferences.data['percent_changed_acceptable'] = 0.30
        else:
            self.my_preferences.data['percent_changed_acceptable'] = 0.10 # default

        if self.one_month_mode.get() == 0: 
            self.my_preferences.data['one_month_mode'] = "FALSE"
        else:
            self.my_preferences.data['one_month_mode'] = "TRUE"

            
        self.my_preferences.writefile(self.config_fname) # write to file
        print("updated preference file: " + self.config_fname)

def exit_handler():
    logging.getLogger().info("==== QCAS Unit Test STOPPED/INTERRUPTED: " + str(datetime.now()) + " by: " + getpass.getuser()  + " ====")
            
def main():
    app = None
    atexit.register(exit_handler)
    
    try: 
        app = qcas_df_gui()
           
    except KeyboardInterrupt:       
        app.root.quit()
        sys.exit(0)

if __name__ == "__main__": main()
