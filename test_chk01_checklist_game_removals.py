import os
import csv
import random
import unittest
import sys
import json
import pickle
import logging
from test_datafiles import QCASTestClient, PSLfile, PSLEntry_OneHash, TSLfile, MSLfile, Preferences, skipping_PSL_comparison_tests, binimage_path_exists
from tkinter import filedialog, Tk


DF_DIRECTORY = "G:/OLGR-TECHSERV/MISC/BINIMAGE/qcas/"

class test_chk01_checklist_game_removals(QCASTestClient):      

    def getGame(self, ssan): 
        currentTSLfile = self.my_preferences.data['TSLfile']
        myTSLfile_list = self.check_file_format(currentTSLfile, 'TSL')
        return_game = Nil
        
        for game in myTSLfile_list: 
            if game.ssan == ssan: 
                return_game = game
                break
        
        return return_game

    # @unittest.skip("TODO: Not yet implemented")
    def test_Games_removed_from_PSL_files(self): 
        previous_TSLfile = self.my_preferences.data['previous_TSLfile']
        currentTSLfile = self.my_preferences.data['TSLfile']
        
        nextMonth_PSLfile = self.my_preferences.data['nextMonth_PSLfile']
        PSLfile = self.my_preferences.data['PSLfile']
        
        verbose_mode = self.my_preferences.data['verbose_mode']
        
        # the verify script can perform checks comparing the differences in the entries of old and new TSL file which 
        # should match with the new and old current month PS1 files – whether additions or removals.
    
        tsl_difference = set()
        with open(previous_TSLfile, 'r') as file1: 
            with open(currentTSLfile, 'r') as file2: 
                tsl_difference = set(file2).difference(file1)
                
        # tsl_difference should now contain added and removed games. 
        if verbose_mode: 
            logging.getLogger().debug("Expected TSL differences: " + str(len(tsl_difference))) 
        
        # build a list of SSAN from TSL objects for comparison
        tsl_ssan_list = list() 
        for tsl_game in tsl_difference: 
            game = TSLfile(tsl_game)
            tsl_ssan_list.append(game.ssan)
                            
        # Generate a list of games removed from PSL files, as the current Month and next Month will have identical SSANs 
        # We will require previous Month's PSL file. 
        
        currentPSLfile = self.check_file_format(PSLfile, 'PSL')              
        Tk().withdraw()        
        # The user must specify the previous month's PSL file which should reflect the changes of the current TSL file.         
        previous_PSLfile = filedialog.askopenfilename(initialdir=DF_DIRECTORY, 
            title = "Select Previous Month PSL File",filetypes = (("PSL files","*.PSL"),("all files","*.*")))            
        
        psl_file_list2 = list() 
        if previous_PSLfile: 
            psl_file_list2 = self.check_file_format(previous_PSLfile, 'PSL')

        # get all ssan in current PSL file
        psl_ssan_in_current_month = list() 
        for psl_file_entry in currentPSLfile:            
            psl_ssan_in_current_month.append(psl_file_entry.ssan) 
        psl_ssan_in_current_month.sort()
        
        # get all ssan in previous month's PSL file
        psl_ssan_in_previous_month = list() 
        for psl_file_entry in psl_file_list2: 
            psl_ssan_in_previous_month.append(psl_file_entry.ssan)  
        psl_ssan_in_previous_month.sort() 
        
        # get the difference between the two sets
        psl_ssan_difference = set(psl_ssan_in_previous_month).symmetric_difference(psl_ssan_in_current_month)

        if verbose_mode: 
            # print("Expected PSL differences: " + str(len(psl_ssan_in_current_month) - len(psl_ssan_in_previous_month)))
            logging.getLogger().debug("Expected PSL differences: " + str(len(psl_ssan_difference)))
        
        err_msg = "Not the same games being added/removed from TSL vs PSL, check you selected the correct previous PSL file."
        self.assertTrue(len(psl_ssan_difference ^ set(tsl_ssan_list)) == 0, msg=err_msg) # bitwise XOR, must be zero fcr matching