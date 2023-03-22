import os
import csv
import random
import unittest
import sys
import json
import pickle
import logging
from test_datafiles import QCASTestClient, PSLfile, PSLEntry_OneHash, TSLfile, MSLfile, \
    Preferences, skipping_PSL_comparison_tests, binimage_path_exists

class test_psl_entry(QCASTestClient):      

    def test_one_game_with_specific_seed(self): 
        # need a TSL game list for one game. 
        tsl_game_l = list() 

        #### Change this ##################################################################################
        # to add more games, add comma separated values here of SSANs. 
        game_ssan_l = [ 239591, 226196 ]        
        assert(len(game_ssan_l) > 0)
        # Note: zero based index, so 0=1 and 9=10, i.e. plus 1; 
        # Additional Note: 1st number is the first month, 2nd number is second month
        test_seed_idx = [ 28, 4 ]                                            
        assert(len(test_seed_idx) == 2)
        ###################################################################################################
        seed_idx = 0

        tslfile_list = self.check_file_format(self.my_preferences.data['TSLfile'], 'TSL')
        assert(len(tslfile_list) > 1), len(tslfile_list)

        for tsl_entry in tslfile_list: 
            # check for game ssan
            for game_ssan in game_ssan_l: 
                if tsl_entry.ssan == game_ssan: 
                    tsl_game_l.append(tsl_entry)
                    break # expect only one entry
        
        assert(len(tsl_game_l) == len(game_ssan_l))
        assert(len(tsl_game_l) > 0)

        for game in tsl_game_l: 
            print(game.toJSON())

        MSLfile = self.my_preferences.data['MSLfile']
        nextMonth_MSLfile = self.my_preferences.data['nextMonth_MSLfile']
        
        PSL_file = self.my_preferences.data['PSLfile']
        nextMonth_PSLfile = self.my_preferences.data['nextMonth_PSLfile']     

        msl_file_list = [MSLfile, nextMonth_MSLfile] 

        for test_game in tsl_game_l: 
            for msl in msl_file_list: 
                mslfile = self.check_file_format(msl, 'MSL') # read in the MSL file
                
                if msl == MSLfile: # first month
                    seed_idx = 0
                else: # second month
                    seed_idx = 1

                test_seed = mslfile[0].seed_list[test_seed_idx[seed_idx]]              
                hash_list_idx = mslfile[0].seed_list.index(test_seed) 
                assert(hash_list_idx == test_seed_idx[seed_idx])

                display_msg = test_game.game_name + " SSAN=" + str(test_game.ssan) + " seed=" + str(test_seed) + " idx=" + str(hash_list_idx+1) + " - " + str(msl) 
                print("\n" + display_msg)
                logging.getLogger().info(display_msg)                    

                blnk_file = os.path.join(self.my_preferences.data['path_to_binimage'], 
                    self.getMID_Directory(test_game.mid), test_game.bin_file.strip() + "." + self.get_bin_type(test_game.bin_type))
                assert(os.path.isfile(blnk_file))

                # get Hash and format to expected output
                localhash = self.getHash(blnk_file, test_seed, hash_list_idx, test_game)
                assert(localhash != None)

                display_msg = "Hash Generated for: " + os.path.basename(blnk_file) + " = [" \
                    + localhash + "] with seed[" + str(hash_list_idx+1) + "]: ["+ self.getQCAS_Expected_output(test_seed) + "]"
                print("\n" + display_msg)
                logging.getLogger().debug(display_msg)

                psl_entries_list = list() 
                # Compare Hash with PSL Entry
                if msl == nextMonth_MSLfile: 
                    psl_entries_list = self.check_file_format(nextMonth_PSLfile, 'PSL')  # read in PSL file
                elif msl == MSLfile: 
                    psl_entries_list = self.check_file_format(PSL_file, 'PSL') 

                # find PSL entry from file to perform comparisons against.
                psl_from_file = None
                for psl_entry in psl_entries_list: 
                    if psl_entry.ssan == test_game.ssan:
                        psl_from_file = psl_entry
                        break 

                msg_str = "Generated Hash: [" + localhash + "] does not equal Expected Hash: [" \
                    +  psl_from_file.hash_list[hash_list_idx] + "] Seed=[" + test_seed + "], Index=" + str(hash_list_idx)                                                      
                # Compare generated hash against the hash from PSL file. 
                self.assertEqual(localhash, psl_from_file.hash_list[hash_list_idx], msg=msg_str)