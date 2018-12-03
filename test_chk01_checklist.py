import os
import csv
import random
import unittest
import sys
import json
import pickle
import logging
from test_datafiles import QCASTestClient, PSLfile, PSLEntry_OneHash, TSLfile, MSLfile, Preferences, skipping_PSL_comparison_tests, binimage_path_exists

class test_chk01_checklist(QCASTestClient):      
    
    def write_to_file(self, fname, data):
            with open(self.my_preferences.data['write_new_games_to_file'], 'w+') as json_file:
                pickle.dump(list(tsl_difference_games_added), outfile)
                # json.dumps(data, json_file, sort_keys=True, indent=4, separators=(',',':'))
                
    # Verifies if current PSL file is not the same as next month's PSL file. 
    @unittest.skipIf(skipping_PSL_comparison_tests(), "Config: Single PSL File Validation") 
    def test_PSL_files_are_Different(self):
        same = set()
        PSL_file = self.my_preferences.data['PSLfile']
        nextMonth_PSLfile = self.my_preferences.data['nextMonth_PSLfile']
        
        with open(PSL_file, 'r') as file1:
            with open(nextMonth_PSLfile, 'r') as file2:
                same = set(file1).intersection(file2)
   
        err_msg = PSL_file + " is the same as: " + nextMonth_PSLfile
        self.assertFalse(len(same) > 0, msg=err_msg)
    
        with open(PSL_file, 'r') as file1:
            with open(nextMonth_PSLfile, 'r') as file2:
                same = set(file1).intersection(file2)
                
    def test_new_games_to_be_added_are_in_PSL_files(self):
        game_list_to_be_added = self.get_newgames_to_be_added()
        PSL_file = self.my_preferences.data['PSLfile']
        nextMonth_PSLfile = self.my_preferences.data['nextMonth_PSLfile']
        
        if self.verbose_mode: 
            if len(game_list_to_be_added) > 0:
                logging.getLogger().debug("==== New Games added ====")
                for tsl_game_item in game_list_to_be_added:                    
                    logging.getLogger().debug(tsl_game_item.toJSON_oneline())
            else:
                logging.getLogger().debug("==== No new games added ==== \n")
                
        # Find these games in the both PSL files

        if skipping_PSL_comparison_tests(): 
            psl_file_list = [PSL_file] 
        else: 
            psl_file_list = [PSL_file, nextMonth_PSLfile] 
        
        verified_game = list()
        
        for psl_file in psl_file_list: 
            psl_entries_list = self.check_file_format(psl_file, 'PSL')       
            
            for game in game_list_to_be_added:      # TSL entries
                for psl_entry in psl_entries_list: 
                    if game.ssan == psl_entry.ssan: # TSL entry SSAN == PSL entry SSAN
                        verified_game.append(game)  # List of TSL entries that have been verified. 
                        break
            
            psl_same = list(set(verified_game).intersection(set(game_list_to_be_added))) 
            
            # For each PSL file does verified_game match game_list_to_be_added? 
            err_msg = "Verified games does not match New Games List from TSL file"
            self.assertTrue(set(verified_game) == set(game_list_to_be_added), msg=err_msg)
            
            #self.assertTrue(set(verified_game).intersection(set(game_list_to_be_added)), 
            #	msg="New PSL entry not found in PSL file") 
            
    # Unit test to address complaints about verifying a complete PSL entry being too slow
    # Note checks both month's MSL and PSL files; only verifies BLNK files. 
    @unittest.skipUnless(binimage_path_exists(), "requires BINIMAGE path")
    def test_X_OLD_games_with_one_seed_in_PSL_file(self): 
        MSLfile = self.my_preferences.data['MSLfile']
        PSL_file = self.my_preferences.data['PSLfile']
        TSLfile = self.my_preferences.data['TSLfile']
        nextMonth_MSLfile = self.my_preferences.data['nextMonth_MSLfile']
        nextMonth_PSLfile = self.my_preferences.data['nextMonth_PSLfile']

        all_games = self.check_file_format(TSLfile, 'TSL')
        
        msl_file_list = list() 
        if skipping_PSL_comparison_tests(): 
            msl_file_list = [MSLfile] 
        else:            
            msl_file_list = [MSLfile, nextMonth_MSLfile] 
            
        complete = False
        count = 1
        random_chosen_game_list = list() # list of randomly selected games
        display_msg = "Testing " + str(self.my_preferences.data['number_of_random_games']) + " old game with random seed"        
        print("\n" + display_msg)
        logging.getLogger().info(display_msg)        
        
        while True: 
            # Choose a Random game from TSL file
            random_tsl_entry = random.choice(all_games) # same for both months
            
            # Test that "BLNK" file contents can be processed, ie. HMAC-SHA1 or SHA1 only. 
            # Will skip if files being hashed in the BLNK is not SHA1, e.g.  CR32, 0A4R, 0A4F 
            if self.check_game_type(random_tsl_entry) == True and random_tsl_entry not in random_chosen_game_list: 
                
                random_chosen_game_list.append(random_tsl_entry) 
                for msl in msl_file_list:
                    mslfile = self.check_file_format(msl, 'MSL')
                                        
                    random_seed_idx =  random.randint(0,30) # Choose a random day for the month
                    random_seed = mslfile[0].seed_list[random_seed_idx]         
                    hash_list_idx = mslfile[0].seed_list.index(random_seed)
                    
                    man_name = self.get_manufacturer_name(random_tsl_entry.mid)
                    msg = "==== Old Game[" + str(count) + "]: " + random_tsl_entry.game_name + \
                        " (" + man_name + "), with MSLfile: [" + os.path.basename(msl) + "] ==== "
                    print("\n" + msg)
                    if self.verbose_mode: 
                        logging.getLogger().debug(msg) #+ random_tsl_entry.toJSON())                    
                    
                    blnk_file = os.path.join(self.my_preferences.data['path_to_binimage'], 
                        self.getMID_Directory(random_tsl_entry.mid), random_tsl_entry.bin_file.strip() + "." + self.get_bin_type(random_tsl_entry.bin_type))
                    
                    # IMPORTANT currently only verifies BLNK files
                    localhash = self.dobnk(blnk_file, random_seed, random_seed_idx, random_tsl_entry.mid, blocksize=65535)
                    
                    # Need to format Hashes
                    tmpStr = str(localhash).lstrip('0X').zfill(40) # forces 40 characters with starting 0 characters. 
                    tmpStr = str(localhash).lstrip('0x').zfill(40)
                    localhash = self.getQCAS_Expected_output(tmpStr).upper() # format it
                    
                    if self.verbose_mode: 
                        display_msg = "Hash Generated for: " + os.path.basename(blnk_file) + " = [" \
                            + localhash + "] with seed: ["+ self.getQCAS_Expected_output(random_seed) + "]"
                        print("\n" + display_msg)
                        logging.getLogger().debug(display_msg)                   

                    psl_entries_list = list() 
                    # Compare Hash with PSL Entry
                    if msl == nextMonth_MSLfile: 
                        psl_entries_list = self.check_file_format(nextMonth_PSLfile, 'PSL')  # generate PSL object list for next month (Important) 
                    elif msl == self.my_preferences.data['MSLfile']: 
                        psl_entries_list = self.check_file_format(PSL_file, 'PSL')  # generate PSL object list for next month (Important) 

                    psl_from_file = ''
                    for psl_entry in psl_entries_list: 
                        if random_tsl_entry.ssan == psl_entry.ssan: 
                            psl_from_file = psl_entry
                            break # not expecting any other matches. 

                    # Compare generated hash against the hash from PSL file. 
                    msg_str = "Generated Hash: [" + localhash + "] does not equal Expected Hash: [" +  \
                        psl_from_file.hash_list[hash_list_idx] + "] Seed=[" + random_seed + "], Index=" + str(hash_list_idx)
                        
                    self.assertEqual(localhash, psl_from_file.hash_list[hash_list_idx], msg=msg_str)

                if count < self.my_preferences.data['number_of_random_games']:
                    count = count + 1
                else:
                    complete = True # set the flag.
                        
            else: 
                if random_tsl_entry not in random_chosen_game_list: 
                    logging.getLogger().info("Skipping: " + random_tsl_entry.game_name + ". Reason: Game already processed, trying another random game.")
                else: 
                    logging.getLogger().info("Skipping: " + random_tsl_entry.game_name + ". Reason: " 
                        + random_tsl_entry.bin_type + " TSL file type, unsupported")

            if complete: 
                break

    # Unit test to address complaints about verifying a complete PSL entry being too slow
    # Note check's both month's PSL and MSL, and only verifies BLNK files. 
    # @unittest.skipUnless(os.path.isdir('\\\\Justice.qld.gov.au\\Data\\OLGR-TECHSERV\\BINIMAGE'), "requires Binimage Path")
    @unittest.skipUnless(binimage_path_exists(), "requires BINIMAGE path")
    def test_X_NEW_game_with_one_seed_in_PSL_file(self): 
        new_games = self.get_newgames_to_be_added()
        msl_file_list = list() 
        
        MSLfile = self.my_preferences.data['MSLfile']
        PSL_file = self.my_preferences.data['PSLfile']
        nextMonth_MSLfile = self.my_preferences.data['nextMonth_MSLfile']
        nextMonth_PSLfile = self.my_preferences.data['nextMonth_PSLfile']
        
        if skipping_PSL_comparison_tests():
            msl_file_list = [MSLfile] 
        else:            
            msl_file_list = [MSLfile, nextMonth_MSLfile] 
            
        complete = False
        count = 1
        number_of_random_games = self.my_preferences.data['number_of_random_games']
        
        display_msg = "Testing " + str(number_of_random_games) + " new game with random seed"
        print("\n" + display_msg)
        logging.getLogger().info(display_msg)
        
        random_chosen_game_list = list() 
        valid_random_game = False

        while True: 
            # Choose a Random game from TSL file              
            random_tsl_entry = random.choice(new_games)            
            
            if len(new_games) < 4: # if < 4 games overall, continue just use different seeds
                valid_random_game = True
            else: # otherwise make sure its not an already tested game
                if random_tsl_entry not in random_chosen_game_list: 
                    valid_random_game = True
                else: 
                    valid_random_game = False
            
            # Test that "BLNK" file contents can be processed, ie. HMAC-SHA1 or SHA1 only. 
            # Will skip if files being hashed in the BLNK is not SHA1, e.g.  CR32, 0A4R, 0A4F 
            if self.check_game_type(random_tsl_entry) == True and valid_random_game == True: 
                random_chosen_game_list.append(random_tsl_entry) # save the game
                valid_random_game = False
                
                for msl in msl_file_list:
                    random_seed_idx =  random.randint(0,30) # Choose a random day for the month
                    mslfile = self.check_file_format(msl, 'MSL')
                    random_seed = mslfile[0].seed_list[random_seed_idx]  
                    hash_list_idx = mslfile[0].seed_list.index(random_seed)

                    man_name = self.get_manufacturer_name(random_tsl_entry.mid)                                
                    display_msg = "==== New Game[" + str(count) + "]: " + random_tsl_entry.game_name \
                        + " (" + man_name + "), with MSLfile: [" + os.path.basename(msl) + "] ==== "                        
                    
                    if self.verbose_mode: 
                        print("\n" + display_msg)
                        logging.getLogger().debug(display_msg)
                                            
                    blnk_file = os.path.join(self.my_preferences.data['path_to_binimage'], 
                    self.getMID_Directory(random_tsl_entry.mid), random_tsl_entry.bin_file.strip() + "." + 
                    self.get_bin_type(random_tsl_entry.bin_type))
                    
                    # IMPORTANT currently only verifies BLNK files
                    if random_tsl_entry.bin_type == "BLNK": 
                        localhash = self.dobnk(blnk_file, random_seed, random_seed_idx, random_tsl_entry.mid, blocksize=65535)
                    else:
                        print("\n")
                        logging.getLogger().error("Trying to Process BLNK file")
                        sys.exit(1) 
                    
                    # Need to format Hashes
                    tmpStr = str(localhash).lstrip('0X').zfill(40) # forces 40 characters with starting 0 characters. 
                    tmpStr = str(localhash).lstrip('0x').zfill(40)
                    localhash = self.getQCAS_Expected_output(tmpStr).upper() # format it
                    
                    if self.verbose_mode: 
                        display_msg = "Hash Generated for: " + os.path.basename(blnk_file) + " = [" \
                            + localhash + "] with seed: ["+ self.getQCAS_Expected_output(random_seed) + "]"
                        print("\n" + display_msg)
                        logging.getLogger().debug(display_msg)                   
                    
                    psl_entries_list = list() 
                    # Compare Hash with PSL Entry
                    if msl == nextMonth_MSLfile: 
                        psl_entries_list = self.check_file_format(nextMonth_PSLfile, 'PSL')  # generate PSL object list for next month (Important) 
                    elif msl == self.my_preferences.data['MSLfile']: 
                        psl_entries_list = self.check_file_format(PSL_file, 'PSL')  # generate PSL object list for next month (Important) 

                    for psl_entry in psl_entries_list: 
                        if random_tsl_entry.ssan == psl_entry.ssan: 
                            psl_from_file = psl_entry
                            break # not expecting any other matches.                             
                    
                    msg_str = "Generated Hash: [" + localhash + "] does not equal Expected Hash: [" \
                        +  psl_from_file.hash_list[hash_list_idx] + "] Seed=[" + random_seed + "], Index=" + str(hash_list_idx)                                                      
                    # Compare generated hash against the hash from PSL file. 
                    self.assertEqual(localhash, psl_from_file.hash_list[hash_list_idx], msg=msg_str)
                    
                if count < number_of_random_games:
                    count = count + 1
                else:
                    complete = True # set the flag.
            else: 
                if not valid_random_game: 
                    logging.getLogger().info("Skipping: " + random_tsl_entry.game_name + ". Reason: Game already processed, trying another random game.")
                else: 
                    logging.getLogger().info("Skipping: " + random_tsl_entry.game_name + ". Reason: " 
                        + random_tsl_entry.bin_type + " TSL file type, unsupported")

            if complete == True: 
                break

        