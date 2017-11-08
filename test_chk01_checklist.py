import os
import csv
import random
import unittest
import sys
from test_datafiles import QCASTestClient, PSLfile, TSLfile, MSLfile

class test_chk01_checklist(QCASTestClient):
   
    def test_Generated_PSL_files_Differ(self):
        same = set()
        
        with open(self.PSLfile, 'r') as file1:
            with open(self.nextMonth_PSLfile, 'r') as file2:
                same = set(file1).intersection(file2)
   
        self.assertFalse(len(same) > 0, 
        	msg=self.PSLfile + " is the same as: " + self.nextMonth_PSLfile)
                
    def test_new_games_to_be_added_are_in_PSL_files(self):
        game_list_to_be_added = self.get_newgames_to_be_added()
            
        # Find these games in the both PSL files
        psl_file_list = [self.PSLfile, self.nextMonth_PSLfile] 
        verified_game = list()
        
        for psl_file in psl_file_list: 
            psl_entries_list = self.check_file_format(psl_file, 'PSL')       
            
            for game in game_list_to_be_added:      #TSL entries
                for psl_entry in psl_entries_list: 
                    if game.ssan == psl_entry.ssan: # TSL entry SSAN == PSL entry SSAN
                        verified_game.append(game)  # List of TSL entries that have been verified. 
            
            # TSL lists            
            psl_difference = list(set(verified_game).intersection(set(game_list_to_be_added))) 
            
            # For each PSL file does verified_game match game_list_to_be_added? 
            self.assertTrue(set(verified_game).intersection(set(game_list_to_be_added)), 
            	msg="New PSL entry not found in PSL file") 
    
    @unittest.skipUnless(os.path.isdir('\\\\Justice.qld.gov.au\\Data\\OLGR-TECHSERV\\BINIMAGE'), 
    	"requires Binimage Path")
    def test_TSL_entries_exist_in_PSL_files(self):        
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
            
            self.assertEqual(len(psl_entry_list), 2) # one PSL entry for each month       

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
            
            # verify that PSL object fields matches is the the PSLfiles  
            self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[0], self.PSLfile), 
            	msg=psl_entry_list[0] + ", entry did not exist in " + self.PSLfile)
            self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[1], self.nextMonth_PSLfile), 
            	msg=psl_entry_list[1] + ", entry did not exist in " + self.nextMonth_PSLfile)
    
    @unittest.skip("TODO: Not yet implemented")
    def test_Games_removed_from_PSL_files(self): 
        # generate a list of games removed. 
        # Difference from previous month PSL and this Months PSL files (multiple). 
        psl_file_list1 = self.check_file_format(self.PSLfile, 'PSL')
        psl_file_list2 = self.check_file_format(self.nextMonth_PSLfile, 'PSL')

        psl_difference = list(set(psl_file_list1).intersection(set(psl_file_list2))) 
    
    # Generate PSL entries for one randomly chosen new game in the new TSL file
    # Compare with PSL files and make sure that entries for both months matches 
    @unittest.skipUnless(os.path.isdir('\\\\Justice.qld.gov.au\\Data\\OLGR-TECHSERV\\BINIMAGE'), 
    	"requires Binimage Path")
    def test_One_new_game_to_be_added_in_PSL_files(self):
        new_games_to_be_added = self.get_newgames_to_be_added()   # TSL object list
        random_tsl_entry = random.choice(new_games_to_be_added) 
        blnk_file = os.path.join(self.my_preferences.path_to_binimage, self.getMID_Directory(random_tsl_entry.mid), 
            random_tsl_entry.bin_file.strip() + "." + self.get_bin_type(random_tsl_entry.bin_type))
        
        psl_entry_list = self.generate_PSL_entry(blnk_file, random_tsl_entry)
                    
        self.assertEqual(len(psl_entry_list), 2, 
        	msg="Expected 2 PSL entries: " + ','.join(psl_entry_list)) # one PSL entry for each month       
        self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[0], self.PSLfile), 
        	msg=psl_entry_list[0] + ", entry did not exist in " + self.PSLfile)
        self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[1], self.nextMonth_PSLfile), 
        	msg=psl_entry_list[1] + ", entry did not exist in " + self.nextMonth_PSLfile)

    # Generate PSL entries for one randomly chosen new game in the new TSL file (all games)
    # Compare with PSL files and make sure that entries for both months matches 
    @unittest.skipUnless(os.path.isdir('\\\\Justice.qld.gov.au\\Data\\OLGR-TECHSERV\\BINIMAGE'), 
    	"requires Binimage Path")
    # @unittest.skip("Debug: Not testing")
    def test_One_old_game_to_be_added_in_PSL_files(self): 
        all_games = self.check_file_format(self.TSLfile, 'TSL') 
        complete = False
        while True: 
            # Choose a Random game from TSL file
            random_tsl_entry = random.choice(all_games)
            
            if random_tsl_entry.bin_file != 'BLNK' and complete == True:
                break
            else: 
                blnk_file = os.path.join(self.my_preferences.path_to_binimage, 
                    self.getMID_Directory(random_tsl_entry.mid), 
                    random_tsl_entry.bin_file.strip() + "." + 
                    str(self.get_bin_type(random_tsl_entry.bin_type)))
                complete = True
                
                psl_entry_list = self.generate_PSL_entry(blnk_file, random_tsl_entry)
                    
                self.assertEqual(len(psl_entry_list), 2, msg="Expected 2 PSL entries: " + ','.join(psl_entry_list)) # one PSL entry for each month       
                self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[0], self.PSLfile), msg=psl_entry_list[0] + ", entry did not exist in " + self.PSLfile)
                self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[1], self.nextMonth_PSLfile), msg=psl_entry_list[1] + ", entry did not exist in " + self.nextMonth_PSLfile)