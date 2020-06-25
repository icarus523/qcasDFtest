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

    def get_all_ssan_in_month(self, f_list): 
        ssan_in_current_month = list() 
        for f_entry in f_list:            
            ssan_in_current_month.append(f_entry.ssan) 
        ssan_in_current_month.sort()
        
        return ssan_in_current_month

    def getDifference_list(self, file1, file2, l_type):         
        
        # difference_set = set() 
        
        # with open(file1, 'r') as f1: 
            # with open(file2, 'r') as f2: 
                # difference_set = set(f2).symmetric_difference(set(f1))
                
        # ssan_list = list() 
        # for item in list(difference_set): 
            # if l_type == 'TSL': 
                # game = TSLfile(item)
                # ssan_list.append(game.ssan)
            # elif l_type == 'PSL': 
                # game = PSLfile(item)
                # ssan_list.append(game.ssan)
       
        
        # return sorted(ssan_list)
        
        f1 = self.check_file_format(file1, l_type)
        f2 = self.check_file_format(file2, l_type)

        # get all ssan in current PSL file
        ssan_in_current_month = self.get_all_ssan_in_month(f1) 
        
        # get all ssan in previous month's PSL file
        ssan_in_previous_month = self.get_all_ssan_in_month(f2)

        # get the difference between the two sets
        ssan_difference = set(ssan_in_previous_month) ^ set(ssan_in_current_month) 
        
        return ssan_difference
        
    def test_Games_removed_from_PSL_files(self): 
        previous_TSLfile = self.my_preferences.data['previous_TSLfile']
        currentTSLfile = self.my_preferences.data['TSLfile']        
        PSLfile = self.my_preferences.data['PSLfile']
        previousMonth_PSLfile = self.my_preferences.data['previousMonth_PSLfile']
                
        if self.verbose_mode: 
            logging.getLogger().info("Testing Games removed from TSL files matches PSL files")
        
        # the verify script can perform checks comparing the differences in the entries of old and new TSL file which 
        # should match with the new and old current month PS1 files – whether additions or removals.    
        tsl_ssan_difference_list = self.getDifference_list(previous_TSLfile, currentTSLfile, 'TSL')
    
        # Generate a list of games removed from PSL files, as the current Month and next Month will have identical SSANs 
        # We will require previous Month's PSL file.        
        psl_ssan_difference_list = self.getDifference_list(PSLfile, previousMonth_PSLfile,'PSL')

        if self.verbose_mode: 
            logging.getLogger().debug("Expected PSL differences: " + str(len(psl_ssan_difference_list)))
            logging.getLogger().debug("Expected TSL differences: " + str(len(tsl_ssan_difference_list)))   
            print("Expected PSL differences: " + str(len(psl_ssan_difference_list)))
            print("Expected TSL differences: " + str(len(tsl_ssan_difference_list)))           
        
        xor_difference =  set(psl_ssan_difference_list) ^ set(tsl_ssan_difference_list) 
        # psl_ssan_difference.symmetric_difference(set(tsl_ssan_list))
        # psl_ssan_difference ^ set(tsl_ssan_list)
        
        if len(xor_difference) != 0: 
            logging.getLogger().debug("Unexpected SSAN differences: " + str(xor_difference)) # display differences in log file

        err_msg = "Not the same games being added/removed from TSL vs PSL. \nCheck you selected the correct previous PSL files: " \
            + previousMonth_PSLfile + " vs " + PSLfile \
            + " \nCheck you selected the correct TSL files: "  + previous_TSLfile + " vs " + currentTSLfile \
            + " \nSSAN differences: " + str(xor_difference)
        
        self.assertTrue(len(xor_difference) == 0, msg=err_msg) # bitwise XOR, must be zero for matching
        
