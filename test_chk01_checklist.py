import os
import csv
import random
import unittest
import sys
import json
import pickle
from test_datafiles import QCASTestClient, PSLfile, TSLfile, MSLfile, Preferences

def skipping_length_tests(): 
    my_preferences = Preferences()
    return my_preferences.will_skip_lengthy_validations()

class test_chk01_checklist(QCASTestClient):      
    
    def write_to_file(self, fname, data):
            with open(self.write_new_games_to_file, 'w+') as json_file:
                pickle.dump(list(tsl_difference_games_added), outfile)
                # json.dumps(data, json_file, sort_keys=True, indent=4, separators=(',',':'))

    def test_Generated_PSL_files_Differ(self):
        same = set()
        
        with open(self.PSLfile, 'r') as file1:
            with open(self.nextMonth_PSLfile, 'r') as file2:
                same = set(file1).intersection(file2)
   
        self.assertFalse(len(same) > 0, 
        	msg=self.PSLfile + " is the same as: " + self.nextMonth_PSLfile)
    
    @unittest.skipIf(skipping_length_tests(), "Skipping Lengthy Validations")            
    def test_new_games_to_be_added_are_in_PSL_files(self):
        game_list_to_be_added = self.get_newgames_to_be_added()
        
        if len(game_list_to_be_added) > 0: 
            print("\n ==== New Games added ====\n")
            for tsl_game_item in game_list_to_be_added:
                print(tsl_game_item.toJSON())    
        else: 
            print("\n ==== No new games added ==== \n")
            
        # Find these games in the both PSL files
        psl_file_list = [self.PSLfile, self.nextMonth_PSLfile] 
        verified_game = list()
        
        for psl_file in psl_file_list: 
            psl_entries_list = self.check_file_format(psl_file, 'PSL')       
            
            for game in game_list_to_be_added:      # TSL entries
                for psl_entry in psl_entries_list: 
                    if game.ssan == psl_entry.ssan: # TSL entry SSAN == PSL entry SSAN
                        verified_game.append(game)  # List of TSL entries that have been verified. 
            
            # TSL lists            
            psl_difference = list(set(verified_game).intersection(set(game_list_to_be_added))) 
            
            # For each PSL file does verified_game match game_list_to_be_added? 
            self.assertTrue(set(verified_game).intersection(set(game_list_to_be_added)), 
            	msg="New PSL entry not found in PSL file") 
    
    @unittest.skipUnless(os.path.isdir('\\\\Justice.qld.gov.au\\Data\\OLGR-TECHSERV\\BINIMAGE'), "requires Binimage Path")
    @unittest.skipIf(skipping_length_tests(), "Skipping Lengthy Validations")            
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
        #psl_file_list2 = self.check_file_format(self.PSLfile, 'PSL')
        #psl_file_list1 = self.check_file_format(self.nextMonth_PSLfile, 'PSL')

        #psl_difference = list(set(psl_file_list1).intersection(set(psl_file_list2))) 
        games_to_be_removed = list() 
        games_to_be_removed = self.get_oldgames_to_be_removed()
        if len(games_to_be_removed) > 1: 
            print("\nIdentified Games removed: ")
            for tsl_game_item in games_to_be_removed:
                print(tsl_game_item.toJSON())
        else:
            print("\nNo Games removed!", end="")
            
    # Generate PSL entries for one randomly chosen new game in the new TSL file
    # Compare with PSL files and make sure that entries for both months matches 
    @unittest.skipUnless(os.path.isdir('\\\\Justice.qld.gov.au\\Data\\OLGR-TECHSERV\\BINIMAGE'), "requires Binimage Path")
    @unittest.skipIf(skipping_length_tests(), "Skipping Lengthy Validations")            
    def test_One_new_game_to_be_added_in_PSL_files_full(self):
        new_games_to_be_added = self.get_newgames_to_be_added()   # TSL object list
        random_tsl_entry = random.choice(new_games_to_be_added) 
        blnk_file = os.path.join(self.my_preferences.path_to_binimage, 
            self.getMID_Directory(random_tsl_entry.mid), 
            random_tsl_entry.bin_file.strip() + "." + self.get_bin_type(random_tsl_entry.bin_type))
        print("\nGenerating PSL entry for one [NEW] approved game: " +  random_tsl_entry.game_name + "; MID: " + random_tsl_entry.mid)

        psl_entry_list = self.generate_PSL_entry(blnk_file, random_tsl_entry)

        for psl_entry in psl_entry_list: 
            print("\n" + psl_entry)
        
        self.assertEqual(len(psl_entry_list), 2, 
        	msg="Expected 2 PSL entries: " + ','.join(psl_entry_list)) # one PSL entry for each month       
        self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[0], self.PSLfile), 
        	msg=psl_entry_list[0] + ", entry did not exist in " + self.PSLfile)
        self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[1], self.nextMonth_PSLfile), 
        	msg=psl_entry_list[1] + ", entry did not exist in " + self.nextMonth_PSLfile)

    # Generate PSL entries for one randomly chosen new game in the new TSL file (all games)
    # Compare with PSL files and make sure that entries for both months matches 
    @unittest.skipUnless(os.path.isdir('\\\\Justice.qld.gov.au\\Data\\OLGR-TECHSERV\\BINIMAGE'), "requires Binimage Path")
    @unittest.skipIf(skipping_length_tests(), "Skipping Lengthy Validations")            
    def test_One_old_game_to_be_added_in_PSL_files_full(self): 
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
                complete = True
                print("\nGenerating PSL entry for one [OLD] approved game: " +  random_tsl_entry.game_name + "; MID: " + random_tsl_entry.mid)

                psl_entry_list = self.generate_PSL_entry(blnk_file, random_tsl_entry) # Slow process
                for psl_entry in psl_entry_list: 
                    print("\n" + psl_entry)    
                    
                self.assertEqual(len(psl_entry_list), 2, msg="Expected 2 PSL entries: " + ','.join(psl_entry_list)) # one PSL entry for each month       
                self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[0], self.PSLfile), msg=psl_entry_list[0] + ", entry did not exist in " + self.PSLfile)
                self.assertTrue(self.verify_psl_entry_exist(psl_entry_list[1], self.nextMonth_PSLfile), msg=psl_entry_list[1] + ", entry did not exist in " + self.nextMonth_PSLfile)
            else: 
                print("\nSkipping: " + random_tsl_entry.game_name + ". Reason: " + random_tsl_entry.bin_type + " file type")
                
    
    # Unit test to address complaints about verifying a complete PSL entry being too slow
    # Note checks both month's MSL and PSL files; only verifies BLNK files. 
    @unittest.skipUnless(os.path.isdir('\\\\Justice.qld.gov.au\\Data\\OLGR-TECHSERV\\BINIMAGE'), "requires Binimage Path")
    def test_One_OLD_game_with_one_seed_in_PSL_file(self): 
        all_games = self.check_file_format(self.TSLfile, 'TSL')
        msl_file_list = [self.MSLfile, self.nextMonth_MSLfile] 

        complete = False
        
        while True: 
            # Choose a Random game from TSL file
            random_tsl_entry = random.choice(all_games) # same for both months
            # Test that "BLNK" file contents can be processed, ie. HMAC-SHA1 or SHA1 only. 
            # Will skip if files being hashed in the BLNK is not SHA1, e.g.  CR32, 0A4R, 0A4F 
            if self.check_game_type(random_tsl_entry) == True: 
                for msl in msl_file_list:
                    random_seed_idx =  random.randint(1,31) # Choose a random day for the month
                    mslfile = self.check_file_format(msl, 'MSL')
                    random_seed = mslfile[0].seed_list[random_seed_idx]         
                    hash_list_idx = mslfile[0].seed_list.index(random_seed)

                    print("\n\n MSLfile: " + msl + " \n ==== Old TSL entry randomly chosen is: ==== \n"+ random_tsl_entry.toJSON())
                    
                    #blnk_file = os.path.join(self.my_preferences.path_to_binimage, 
                    #        self.getMID_Directory(random_tsl_entry.mid), 
                    #        random_tsl_entry.bin_file.strip() 
                    #        + "." + str(self.get_bin_type(random_tsl_entry.bin_type)))

                    blnk_file = os.path.join(self.my_preferences.path_to_binimage, 
                    self.getMID_Directory(random_tsl_entry.mid), random_tsl_entry.bin_file.strip() + "." + 
                    self.get_bin_type(random_tsl_entry.bin_type))
                    
                    # IMPORTANT currently only verifies BLNK files
                    if random_tsl_entry.bin_type == "BLNK": 
                        localhash = self.dobnk(blnk_file, random_seed, random_seed_idx, random_tsl_entry.mid, blocksize=65535)
                    else:
                        print("Trying to Process BLNK file") # Shouldn't get here
                        sys.exit(1) 
                    
                    # Need to format Hashes
                    tmpStr = str(localhash).lstrip('0X').zfill(40) # forces 40 characters with starting 0 characters. 
                    tmpStr = str(localhash).lstrip('0x').zfill(40)
                    localhash = self.getQCAS_Expected_output(tmpStr).upper() # format it
                    
                    psl_entries_list = list() 
                    # Compare Hash with PSL Entry
                    if msl == self.nextMonth_MSLfile: 
                        psl_entries_list = self.check_file_format(self.nextMonth_PSLfile, 'PSL')  # generate PSL object list for next month (Important) 
                    elif msl == self.MSLfile: 
                        psl_entries_list = self.check_file_format(self.PSLfile, 'PSL')  # generate PSL object list for next month (Important) 

                    for psl_entry in psl_entries_list: 
                        if random_tsl_entry.ssan == psl_entry.ssan: 
                            psl_from_file = psl_entry
                            break # not expecting any other matches. 

                    # Compare generated hash against the hash from PSL file. 
                    self.assertEqual(localhash, psl_from_file.hash_list[hash_list_idx], msg="seed: " + random_seed + " idx=" + str(hash_list_idx))
                        
                    complete = True # set the flag.

            else: 
                print("\nSkipping: " + random_tsl_entry.game_name + ". Reason: " 
                    + random_tsl_entry.bin_type + " file type, can't be processed at this time")

            if complete == True: 
                break

    # Unit test to address complaints about verifying a complete PSL entry being too slow
    # Note check's both month's PSL and MSL, and only verifies BLNK files. 
    @unittest.skipUnless(os.path.isdir('\\\\Justice.qld.gov.au\\Data\\OLGR-TECHSERV\\BINIMAGE'), "requires Binimage Path")
    def test_One_NEW_game_with_one_seed_in_PSL_file(self): 
        new_games = self.get_newgames_to_be_added()
        msl_file_list = [self.MSLfile, self.nextMonth_MSLfile] 

        complete = False
        
        while True: 
            # Choose a Random game from TSL file
            random_tsl_entry = random.choice(new_games) # same for both months
            # Test that "BLNK" file contents can be processed, ie. HMAC-SHA1 or SHA1 only. 
            # Will skip if files being hashed in the BLNK is not SHA1, e.g.  CR32, 0A4R, 0A4F 
            if self.check_game_type(random_tsl_entry) == True: 
                for msl in msl_file_list:
                    random_seed_idx =  random.randint(1,31) # Choose a random day for the month
                    mslfile = self.check_file_format(msl, 'MSL')
                    random_seed = mslfile[0].seed_list[random_seed_idx]  
                    print("random_seed_idx: " +  str(random_seed_idx))
                    hash_list_idx = mslfile[0].seed_list.index(random_seed)

                    print("\n\n MSLfile: " + msl + " \n ==== New TSL entry randomly chosen is: ==== \n"+ random_tsl_entry.toJSON())
            

                    blnk_file = os.path.join(self.my_preferences.path_to_binimage, 
                    self.getMID_Directory(random_tsl_entry.mid), random_tsl_entry.bin_file.strip() + "." + 
                    self.get_bin_type(random_tsl_entry.bin_type))
                    
                    # IMPORTANT currently only verifies BLNK files
                    if random_tsl_entry.bin_type == "BLNK": 
                        localhash = self.dobnk(blnk_file, random_seed, random_seed_idx, random_tsl_entry.mid, blocksize=65535)
                    else:
                        print("Trying to Process BLNK file") # Shouldn't get here
                        sys.exit(1) 
                    
                    # Need to format Hashes
                    tmpStr = str(localhash).lstrip('0X').zfill(40) # forces 40 characters with starting 0 characters. 
                    tmpStr = str(localhash).lstrip('0x').zfill(40)
                    localhash = self.getQCAS_Expected_output(tmpStr).upper() # format it
                    
                    psl_entries_list = list() 
                    # Compare Hash with PSL Entry
                    if msl == self.nextMonth_MSLfile: 
                        psl_entries_list = self.check_file_format(self.nextMonth_PSLfile, 'PSL')  # generate PSL object list for next month (Important) 
                    elif msl == self.MSLfile: 
                        psl_entries_list = self.check_file_format(self.PSLfile, 'PSL')  # generate PSL object list for next month (Important) 

                    for psl_entry in psl_entries_list: 
                        if random_tsl_entry.ssan == psl_entry.ssan: 
                            psl_from_file = psl_entry
                            break # not expecting any other matches. 

                    # Compare generated hash against the hash from PSL file. 
                    self.assertEqual(localhash, psl_from_file.hash_list[hash_list_idx], msg="seed: " + random_seed + " idx=" + str(hash_list_idx))
                        
                    complete = True # set the flag.

            else: 
                print("\nSkipping: " + random_tsl_entry.game_name + ". Reason: " 
                    + random_tsl_entry.bin_type + " file type, can't be processed at this time")

            if complete == True: 
                break