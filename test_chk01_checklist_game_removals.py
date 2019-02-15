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

    def getTSLDifference_List(self, previous_TSLfile, currentTSLfile): 
        tsl_difference = set()

        with open(previous_TSLfile, 'r') as file1: 
            with open(currentTSLfile, 'r') as file2: 
                tsl_difference = set(file2).symmetric_difference(set(file1))
                
        # tsl_difference should now contain added and removed games. 
        if self.verbose_mode: 
            logging.getLogger().debug("Expected TSL differences: " + str(len(tsl_difference)))   
        
        # build a list of SSAN from TSL objects for comparison
        tsl_ssan_list = list() 
        for tsl_game in tsl_difference: 
            game = TSLfile(tsl_game)
            tsl_ssan_list.append(game.ssan)
        
        return tsl_ssan_list

    def getPSLDifference_List(self, PSLfile, previous_PSLfile):         
        currentPSLfile = self.check_file_format(PSLfile, 'PSL')
        prevPSLfile = self.check_file_format(previous_PSLfile, 'PSL')

        # get all ssan in current PSL file
        psl_ssan_in_current_month = list() 
        for psl_file_entry in currentPSLfile:            
            psl_ssan_in_current_month.append(psl_file_entry.ssan) 
        psl_ssan_in_current_month.sort()
        
        # get all ssan in previous month's PSL file
        psl_ssan_in_previous_month = list() 
        for psl_file_entry in prevPSLfile: 
            psl_ssan_in_previous_month.append(psl_file_entry.ssan)  
        psl_ssan_in_previous_month.sort() 
        
        # get the difference between the two sets
        psl_ssan_difference = set(psl_ssan_in_previous_month).symmetric_difference(psl_ssan_in_current_month)        
        
        return psl_ssan_difference
        
    def test_Games_removed_from_PSL_files(self): 
        previous_TSLfile = self.my_preferences.data['previous_TSLfile']
        currentTSLfile = self.my_preferences.data['TSLfile']        
        PSLfile = self.my_preferences.data['PSLfile']
        previousMonth_PSLfile = self.my_preferences.data['previousMonth_PSLfile']
                
        if self.verbose_mode: 
            logging.getLogger().info("Testing Games removed from TSL files matches PSL files")
        
        # the verify script can perform checks comparing the differences in the entries of old and new TSL file which 
        # should match with the new and old current month PS1 files – whether additions or removals.    
        tsl_ssan_list = self.getTSLDifference_List(previous_TSLfile, currentTSLfile)
    
        # Generate a list of games removed from PSL files, as the current Month and next Month will have identical SSANs 
        # We will require previous Month's PSL file.        
        psl_ssan_difference = self.getPSLDifference_List(PSLfile, previousMonth_PSLfile)

        if self.verbose_mode: 
            logging.getLogger().debug("Expected PSL differences: " + str(len(psl_ssan_difference)))
        
        err_msg = "Not the same games being added/removed from TSL vs PSL, check you selected the correct previous PSL file: " + previousMonth_PSLfile
        xor_difference =  psl_ssan_difference ^ set(tsl_ssan_list)                # psl_ssan_difference.symmetric_difference(set(tsl_ssan_list))# 
        if len(xor_difference) != 0: 
            logging.getLogger().debug("Unexpected SSAN differences: " + str(xor_difference))
            
        self.assertTrue(len(xor_difference) == 0, msg=err_msg) # bitwise XOR, must be zero fcr matching
        
