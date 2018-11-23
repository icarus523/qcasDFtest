import tkinter as tk
import threading
import subprocess
import json
import getpass
import glob
import os
import hashlib
import logging

from datetime import datetime
from tkinter import *
from tkinter import ttk
from tkinter import filedialog

from test_datafiles import QCASTestClient, PSLfile, PSLEntry_OneHash, TSLfile, MSLfile, Preferences, skipping_PSL_comparison_tests, binimage_path_exists

VERSION = "0.1"

class qcas_df_gui: 

    # Constructor
    def __init__(self):
        self.my_preferences = Preferences() 
        self.root = tk.Tk()       
        self.config_fname = "preferences.dat"
        
        menubar = tk.Menu(self.root)
        filemenu = tk.Menu(menubar, tearoff=0)
        optionmenu = tk.Menu(menubar, tearoff=0)

        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Exit", command=self.root.destroy)
        
        self.root.config(menu=menubar)
        threading.Thread(self.setUpGUI()).start()        

    ############# GUI Related ################## 
    def setUpGUI(self):
        self.root.wm_title("QCAS DF Verify Control v" + VERSION)        
        
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
        v_msl.set(self.my_preferences.MSLfile)
        self.tf_current_msl.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)

        ######## Next Month MSL
        frame_next_month_msl = ttk.Frame(frame_toparea)
        frame_next_month_msl.config(relief = FLAT, borderwidth = 1)
        frame_next_month_msl.pack(side = TOP, padx  = 0, pady = 0, expand = False, fill=X, anchor = 'w')       

        # Button Next Month MSL file
        button_select_nextmonth_msl = ttk.Button(frame_next_month_msl, text = "Next Month MSL File...", width=20, 
            command = lambda: self.handleButtonPress('__select_nextmonth_msl_file__'))                                             
        button_select_nextmonth_msl.pack(side=LEFT, padx = 3, pady = 3, fill=X, expand=False)        
        # Text Entry Current MSL file
        v = StringVar() 
        self.tf_nextmonth_msl = ttk.Entry(frame_next_month_msl, width = 100, textvariable = v)
        v.set(self.my_preferences.nextMonth_MSLfile)
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
        v_psl.set(self.my_preferences.PSLfile)
        self.tf_current_psl.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)

        ######## Next Month PSL
        frame_next_month_psl = ttk.Frame(frame_toparea)
        frame_next_month_psl.config(relief = FLAT, borderwidth = 1)
        frame_next_month_psl.pack(side = TOP, padx  = 0, pady = 0, expand = False, fill=X, anchor = 'w')       

        # Button Next Month PSL file
        button_select_nextmonth_msl = ttk.Button(frame_next_month_psl, text = "Next Month PSL File...", width=20, 
            command = lambda: self.handleButtonPress('__select_nextmonth_psl_file__'))                                             
        button_select_nextmonth_msl.pack(side=LEFT, padx = 3, pady = 3, fill=X, expand=False)        
        # Text Next Month PSL file
        v_psl2 = StringVar() 
        self.tf_nextmonth_psl = ttk.Entry(frame_next_month_psl, width = 100, textvariable = v_psl2)
        v_psl2.set(self.my_preferences.nextMonth_PSLfile)
        self.tf_nextmonth_psl.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)


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
        v_tsl.set(self.my_preferences.TSLfile)
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
        v_tsl2.set(self.my_preferences.previous_TSLfile)
        self.tf_previousmonth_tsl.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)

        #Frame for Config
        frame_config = ttk.Labelframe(frame_toparea, text="Configuration")
        frame_config.pack(side = TOP, fill=Y, expand = False)
        frame_config.config(relief = RIDGE, borderwidth = 2)
        
        ######## BINIMAGE Location
        frame_binimage = ttk.Frame(frame_config)
        frame_binimage.config(relief = FLAT, borderwidth = 1)
        frame_binimage.grid(row=1, column=1, sticky='w')

        # Button Binimage Path
        button_binimage_path = ttk.Button(frame_binimage, text = "BINIMAGE PATH...", width=20, 
            command = lambda: self.handleButtonPress('__select_binimage__'))                                             
        button_binimage_path.pack(side=LEFT, padx = 3, pady = 3, fill=X, expand=False)        
        # Text Binimage Path
        self.v_binimage = StringVar() 
        self.tf_binimage_path= ttk.Entry(frame_binimage, width = 100, textvariable = self.v_binimage)
        self.v_binimage.set(self.my_preferences.path_to_binimage)
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
        self.v_epsiglog.set(self.my_preferences.epsig_log_file)
        self.tf_epsiglog_path.pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)

        # Combobox Number of Games to Validate
        frame_combobox = ttk.Frame(frame_config)
        frame_combobox.config(relief = FLAT, borderwidth = 1)
        frame_combobox.grid(row=3, column=1, sticky='w')
        
        self.box_value = IntVar()
        ttk.Label(frame_combobox, justify=LEFT, text = 'Number of Games To Validate: ').pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)
        self.combobox_NumberofGames = ttk.Combobox(frame_combobox, 
            justify=LEFT, 
            textvariable=self.box_value)
        self.combobox_NumberofGames.pack(side=RIGHT, fill=X, padx = 3, pady = 3, expand=True)
        self.combobox_NumberofGames.set(self.my_preferences.number_of_random_games) # default value
        self.combobox_NumberofGames['values'] = ['1', '2', '3', '4', '5', '10', '20']

        # Combobox Acceptable Percentage Change to a PSL file
        frame_combobox_psl_change = ttk.Frame(frame_config)
        frame_combobox_psl_change.config(relief = FLAT, borderwidth = 1)
        frame_combobox_psl_change.grid(row=4, column=1, sticky='w')
        
        self.box_value2 = StringVar()
        ttk.Label(frame_combobox_psl_change, justify=LEFT, text = 'PSL file size changed threshold: ').pack(side=LEFT, fill=X, padx = 3, pady = 3, expand=True)
        self.combobox_NumberofGames = ttk.Combobox(frame_combobox_psl_change, 
            justify=LEFT, 
            textvariable=self.box_value2)
        self.combobox_NumberofGames.pack(side=RIGHT, fill=X, padx = 3, pady = 3, expand=True)
        def_val = str(self.my_preferences.percent_changed_acceptable*100) + "%"
        self.combobox_NumberofGames.set(def_val) # default value
        self.combobox_NumberofGames['values'] = ['5%','10%', '20%', '30%']
        
        # Checkbutton Intensive Validation
        self.intensive_validation = IntVar()
        if self.my_preferences.skip_lengthy_validations == "false":
            self.intensive_validation.set(0)
        else:
            self.intensive_validation.set(1)
        self.cb_intensive_validation = Checkbutton(
            frame_config, 
            text="Skip Intensive Validations", 
            justify=LEFT, 
            variable = self.intensive_validation, 
            onvalue=1, 
            offvalue=0)
        self.cb_intensive_validation.grid(row=5, column=1, sticky='w')

        # Checkbutton Verbose Mode
        self.verbose_mode = IntVar()
        if self.my_preferences.verbose_mode == "false":
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
        self.cb_verbose_mode.grid(row=6, column=1, sticky='w')

        ######## Bottom Frame
        frame_bottomarea = ttk.Frame(self.root)
        frame_bottomarea.pack(side = BOTTOM, fill=X, expand=False)
        frame_bottomarea.config(relief = RIDGE, borderwidth = 1)

        ######## Start Button Frame
        frame_start_button = ttk.Frame(frame_bottomarea)
        frame_start_button.config(relief = FLAT, borderwidth = 1)
        frame_start_button.pack(side = TOP, padx  = 0, pady = 0, expand = False, fill=X, anchor = 'w')       
        # Button Start 
        button_start = ttk.Button(frame_start_button, text = "Start Verification", width=20, 
            command = lambda: self.handleButtonPress('__start__'))
        button_start.pack(side=RIGHT, padx = 3, pady = 3, fill=X, expand=False)       
        # Button Save Config 
        button_save = ttk.Button(frame_start_button, text = "Save Config", width=20, 
            command = lambda: self.handleButtonPress('__save__'))                 
        button_save.pack(side=LEFT, padx = 3, pady = 3, fill=X, expand=False)       

        self.root.mainloop()

    def handleButtonPress(self, choice):
        if choice == '__select_current_msl_file__':
            tmp = filedialog.askopenfile(initialdir='.')
            
            if tmp: # Selected something
                self.tf_current_msl.delete(0, END)
                self.tf_current_msl.insert(0, tmp.name)                
        elif choice == '__select_nextmonth_msl_file__':
            tmp = filedialog.askopenfile(initialdir='.')
            
            if tmp: # Selected something
                self.tf_nextmonth_msl.delete(0, END)
                self.tf_nextmonth_msl.insert(0, tmp.name)
        elif choice == '__select_psl_file__':
            tmp = filedialog.askopenfile(initialdir='.')
            
            if tmp: # Selected something
                self.tf_current_psl.delete(0, END)                
                self.tf_current_psl.insert(0, tmp.name)
        elif choice == '__select_nextmonth_psl_file__':
            tmp = filedialog.askopenfile(initialdir='.')
            
            if tmp: # Selected something
                self.tf_nextmonth_psl.delete(0, END)                                
                self.tf_nextmonth_psl.insert(0, tmp.name)
        elif choice == '__select_tsl_file__':
            tmp = filedialog.askopenfile(initialdir='.')
            
            if tmp: # Selected something
                self.tf_current_tsl.delete(0, END)                                                
                self.tf_current_tsl.insert(0, tmp.name)

        elif choice == '__select_previousmonth_tsl_file__':
            tmp = filedialog.askopenfile(initialdir='.')
            
            if tmp: # Selected something
                self.tf_previousmonth_tsl.delete(0, END)                                
                self.tf_previousmonth_tsl.insert(0, tmp.name)
                
        elif choice == '__select_binimage__':
            tmp = filedialog.askdirectory(initialdir=self.my_preferences.path_to_binimage)
            
            if tmp: # Selected something
                self.tf_binimage_path.delete(0, END)                                
                self.tf_binimage_path.insert(0, tmp)

        elif choice == '__select_epsiglog_file__':
            tmp = filedialog.askdirectory(initialdir='.')
            
            if tmp: # Selected something
                self.tf_epsiglog_path.delete(0, END)                                
                self.tf_epsiglog_path.insert(0, tmp)
                
        elif choice == '__start__':
            threading.Thread(self.StartUnitTest()).start()        

        elif choice == '__save__':
            self.UpdatePreferences()

    def StartUnitTest(self):
        # subprocess.call('py __start_qcas_unittesting_script.py', shell=False)
        def_str = "==== QCAS Unit Testing started on: " + str(datetime.now()) + " by: " + getpass.getuser()  + " ===="
        logging.getLogger().info(def_str)    

        config = json.dumps(self.my_preferences.data, sort_keys=True, indent=4, separators=(',', ': '))
        logging.getLogger().info("QCAS Unit Testing Configuration: \n" + config)

        logging.getLogger().info("==== QCAS Unit Test script versions: ====")
        unit_test_files = glob.glob("test*.py")
        for file in unit_test_files:
            logging.getLogger().info("%35s\t%s" % (file, QCASTestClient.dohash_sha256(self, file)))
        logging.getLogger().info("==== Starting Unit Tests ====")
        subprocess.call('py -m unittest', shell=False)



    def UpdatePreferences(self):        
        #update vars
        self.my_preferences.previous_TSLfile = self.tf_previousmonth_tsl.get()
        self.my_preferences.TSLfile = self.tf_current_tsl.get() 
        self.my_preferences.PSLfile = self.tf_current_psl.get()
        self.my_preferences.nextMonth_PSLfile = self.tf_nextmonth_psl.get()
        self.my_preferences.MSLfile = self.tf_current_msl.get()
        self.my_preferences.nextMonth_MSLfile = self.tf_nextmonth_msl.get()
        self.my_preferences.path_to_binimage = self.v_binimage.get()
        self.my_preferences.number_of_random_games = self.box_value.get()
        self.my_preferences.epsig_log_file = self.v_epsiglog.get()        
        
        if self.intensive_validation.get() == 0: 
            self.my_preferences.skip_lengthy_validations = "false"
        else:
            self.my_preferences.skip_lengthy_validations = "true"            

        if self.verbose_mode.get() == 0:
            self.my_preferences.verbose_mode = "false"
        else:
            self.my_preferences.verbose_mode = "true"

        if self.box_value2.get() == '5%': 
            self.my_preferences.percent_changed_acceptable = 0.05
        elif self.box_value2.get() == '10%':
            self.my_preferences.percent_changed_acceptable = 0.10
        elif self.box_value2.get() == '20%':
            self.my_preferences.percent_changed_acceptable = 0.20
        elif self.box_value2.get() == '30%':
            self.my_preferences.percent_changed_acceptable = 0.30
        else:
            self.my_preferences.percent_changed_acceptable = 0.10 # default

                    
        self.my_preferences.writefile(self.config_fname) # write to file
        print(self.my_preferences.toJSON())
        print("updated preference file: " + self.config_fname)
            
def main():
    app = None
    
    try: 
        app = qcas_df_gui()
           
    except KeyboardInterrupt:       
        logging.debug("Program Exiting.")
        app.root.quit()

        sys.exit(0)

if __name__ == "__main__": main()
