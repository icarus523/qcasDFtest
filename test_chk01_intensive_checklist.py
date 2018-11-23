import os
import csv
import random
import unittest
import sys
import json
import pickle
import logging
from test_datafiles import QCASTestClient, PSLfile, PSLEntry_OneHash, TSLfile, MSLfile, Preferences, skipping_PSL_comparison_tests, binimage_path_exists

def skipping_length_tests(): 
    my_preferences = Preferences()
    return my_preferences.will_skip_lengthy_validations()

class test_chk01_intensive_checklist(QCASTestClient):      

    @unittest.skipUnless(binimage_path_exists(), "requires Binimage Path")
    @unittest.skipIf(skipping_length_tests(), "Skipping Lengthy Validations")        
    def test_TSL_entries_exist_in_PSL_files_full(self):       
        if self.my_preferences.verbose_mode == "true": 
            logging.getLogger().info("Testing new Games are in PSL files (full)")    
        # Read TSL entry
        # Generate PSL entry with seeds
        # Find that this PSL entry exits in PSL file. 
        psl_object_list = list()
        
        TSL_game_list_to_be_added = self.get_newgames_to_be_added()
        count = 0
        
        for game in TSL_game_list_to_be_added: 
            blnk_file = os.path.join(self.my_preferences.path_to_binimage, 
            	self.getMID_Directory(game.mid), game.bin_file.strip() + "." + 
            	self.get_bin_type(game.bin_type))
            
            psl_entry_list = self.generate_PSL_entry(blnk_file, game)
            
            if not skipping_PSL_comparison_tests():
                self.assertEqual(len(psl_entry_list), 2) # one PSL entry for each month       
            else: 
                self.assertEqual(len(psl_entry_list), 1) # one month only       

            for psl_entry in psl_entry_list: 
                psl_entry_object = PSLfile(psl_entry) 

                self.assertTrue(len(psl_entry_object.game_name) < 31, 
                	msg="Game Name has to be 30 characters or less")
                self.assertTrue(psl_entry_object.manufacturer in self.my_preferences.mid_list, 
                	msg="Not a valid MID")
            
                valid_year = list(range(2017,9999))
                self.assertTrue(psl_entry_object.year in valid_year, 
                	msg="Year Field not in range: 2017 < " + str(psl_entry_object.year) + " < 9999" )
            
                valid_months = list(range(1,13))
                self.assertTrue(psl_entry_object.month in valid_months, 
                	msg="Not a valid month: " + str(psl_entry_object.month))
        
                #valid_ssan = list (range(150000, 999999999)) # run out of memory here
                self.assertTrue(psl_entry_object.ssan < 999999999 and psl_entry_object.ssan > 150000)
            
                self.assertTrue(len(psl_entry_object.hash_list) == 31, 
                	msg="Hashlist doesn't contain 31 hashes")
            
            if not skipping_PSL_comparison_tests():
                # verify that PSL object fields matches is the the PSLfiles  
                self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[0], self.PSLfile), 
                    msg=psl_entry_list[0] + ", entry did not exist in " + self.PSLfile)
                self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[1], self.nextMonth_PSLfile), 
                    msg=psl_entry_list[1] + ", entry did not exist in " + self.nextMonth_PSLfile)
            else: 
                self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[0], self.PSLfile), 
                    msg=psl_entry_list[0] + ", entry did not exist in " + self.PSLfile)

    # Generate PSL entries for one randomly chosen new game in the new TSL file
    # Compare with PSL files and make sure that entries for both months matches 
    @unittest.skipUnless(binimage_path_exists(), "requires Binimage Path")
    @unittest.skipIf(skipping_length_tests(), "Skipping Lengthy Validations")            
    def test_One_new_game_to_be_added_in_PSL_files_full(self):
        if self.my_preferences.verbose_mode == "true": 
            logging.getLogger().info("Testing One New Game Entry in PSL file (full)")
        
        new_games_to_be_added = self.get_newgames_to_be_added()   # TSL object list
        random_tsl_entry = random.choice(new_games_to_be_added) 
        blnk_file = os.path.join(self.my_preferences.path_to_binimage, 
            self.getMID_Directory(random_tsl_entry.mid), 
            random_tsl_entry.bin_file.strip() + "." + self.get_bin_type(random_tsl_entry.bin_type))
            
        if self.my_preferences.verbose_mode == "true": 
            man_name = self.get_manufacturer_name(random_tsl_entry.mid)                                
            logging.getLogger().debug("Generating PSL entry for one [NEW] approved game: " +  random_tsl_entry.game_name + " (" + man_name + ")")

        psl_entry_list = self.generate_PSL_entry(blnk_file, random_tsl_entry)

        if self.my_preferences.verbose_mode == "true": 
            for psl_entry in psl_entry_list: 
                logging.getLogger().debug(psl_entry)
        
        if not skipping_PSL_comparison_tests():
            self.assertEqual(len(psl_entry_list), 2, 
                msg="Expected 2 PSL entries: " + ','.join(psl_entry_list)) # one PSL entry for each month       
            self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[0], self.PSLfile), 
                msg=psl_entry_list[0] + ", entry did not exist in " + self.PSLfile)
            self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[1], self.nextMonth_PSLfile), 
                msg=psl_entry_list[1] + ", entry did not exist in " + self.nextMonth_PSLfile)
        else: 
            self.assertEqual(len(psl_entry_list), 1, msg="Expected 1 PSL entries: " + ','.join(psl_entry_list))
            self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[0], self.PSLfile), 
                msg=psl_entry_list[0] + ", entry did not exist in " + self.PSLfile)

    # Generate PSL entries for one randomly chosen new game in the new TSL file (all games)
    # Compare with PSL files and make sure that entries for both months matches 
    @unittest.skipUnless(binimage_path_exists(), "requires Binimage Path")
    @unittest.skipIf(skipping_length_tests(), "Skipping Lengthy Validations")            
    def test_One_old_game_to_be_added_in_PSL_files_full(self): 
        if self.my_preferences.verbose_mode == "true": 
            logging.getLogger().info("Testing One Old Game Entry in PSL file (full)")
        
        all_games = self.check_file_format(self.TSLfile, 'TSL') 
        complete = False
        while True: 
            # Choose a Random game from TSL file
            random_tsl_entry = random.choice(all_games)
            
            if random_tsl_entry.bin_type == 'BLNK' and complete == True:
                break
            
            if random_tsl_entry.bin_type == 'BLNK': 
                blnk_file = os.path.join(self.my_preferences.path_to_binimage, 
                    self.getMID_Directory(random_tsl_entry.mid), 
                    random_tsl_entry.bin_file.strip() + "." + 
                    str(self.get_bin_type(random_tsl_entry.bin_type)))
                    
                # Read BNK file and test if its parsible, i.e. only SHA1
                with open(blnk_file, 'r') as file:         
                    field_names = ['fname', 'type', 'blah']
                    reader = csv.DictReader(file, delimiter=' ', fieldnames=field_names)
                
                    for row in reader: 
                        if row['type'].upper() != 'SHA1': # To handle CR32, 0A4R, 0A4F           
                            complete = False
                            break
                        else: 
                            complete = True
                            
                if self.my_preferences.verbose_mode == "true" and complete == True: 
                    man_name = self.get_manufacturer_name(random_tsl_entry.mid)                                
                    logging.getLogger().debug("Generating PSL entry for one [OLD] approved game: " +  random_tsl_entry.game_name + " (" + man_name + ")")

                if complete: 
                    psl_entry_list = self.generate_PSL_entry(blnk_file, random_tsl_entry) # Slow process

                if self.my_preferences.verbose_mode == "true" and complete: 
                    for psl_entry in psl_entry_list: 
                        logging.getLogger().debug(psl_entry)    
                
                if not skipping_PSL_comparison_tests():
                    self.assertEqual(len(psl_entry_list), 2, msg="Expected 2 PSL entries: " + ','.join(psl_entry_list)) # one PSL entry for each month       
                    self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[0], self.PSLfile), msg=psl_entry_list[0] + ", entry did not exist in " + self.PSLfile)
                    self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[1], self.nextMonth_PSLfile), msg=psl_entry_list[1] + ", entry did not exist in " + self.nextMonth_PSLfile)
                else: 
                    self.assertEqual(len(psl_entry_list), 1, msg="Expected 1 PSL entries: " + ','.join(psl_entry_list)) # one PSL entry for each month       
                    self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[0], self.PSLfile), msg=psl_entry_list[0] + ", entry did not exist in " + self.PSLfile)
            else: 
                if self.my_preferences.verbose_mode == "true": 
                    logging.getLogger().debug("Skipping: " + random_tsl_entry.game_name + ". Reason: " + random_tsl_entry.bin_type + " file type")                    