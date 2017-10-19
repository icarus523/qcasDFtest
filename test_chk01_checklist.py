import os
import csv

from test_datafiles import QCASTestClient, PSLfile, TSLfile, MSLfile

MID_LIST = [ '00', '01', '05', '07', '09', '12', '17']

class test_chk01_checklist(QCASTestClient):
   
    def test_Generated_PSL_files_Differ(self):
        same = set()
        
        with open(self.PSLfile, 'r') as file1:
            with open(self.nextMonth_PSLfile, 'r') as file2:
                same = set(file1).intersection(file2)
   
        self.assertFalse(len(same) > 0)
                
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
                        
            psl_difference = list(set(verified_game).intersection(set(game_list_to_be_added))) # TSL lists
            #for tslitem in psl_difference: 
            #    print("Verified added games in " + psl_file + " is: " + tslitem.game_name)
                
            self.assertTrue(set(verified_game).intersection(set(game_list_to_be_added)))
    
    def test_TSL_entries_exist_in_PSL_files(self):        
        # Read TSL entry
        # Generate PSL entry with seeds
        # Find that this PSL entry exits in PSL file. 
        psl_object_list = list()
        
        TSL_game_list_to_be_added = self.get_newgames_to_be_added()
        both_MSL_seed_list_file = [self.MSLfile , self.nextMonth_MSLfile] 
        for MSL_file in both_MSL_seed_list_file: 
            count = 0
            for game in TSL_game_list_to_be_added: 
                psl_entry_string = self.generate_PSL_entries(MSL_file, game) 
                print("\n" + psl_entry_string)
                
                # test the psl_entry to be formatted as an PSL object
                psl_entry_object = PSLfile(psl_entry_string) 
                
                self.assertTrue(len(psl_entry_object.game_name) < 31)
                self.assertTrue(psl_entry_object.manufacturer in MID_LIST)
                
                valid_year = list(range(2017,9999))
                self.assertTrue(psl_entry_object.year in valid_year)
                
                valid_months = list(range(1,13))
                self.assertTrue(psl_entry_object.month in valid_months)
            
                #valid_ssan = list (range(150000, 999999999))
                self.assertTrue(psl_entry_object.ssan < 999999999 and psl_entry_object.ssan > 150000)
                
                self.assertTrue(len(psl_entry_object.hash_list) == 31)
                
                # verify that PSL object fields matches is the the PSLfiles  
                psl_files_list = [self.PSLfile, self.nextMonth_PSLfile] 
                for psl_file in psl_files_list:
                    if self.verify_psl_entry_exist(psl_entry_object.toString(), psl_file): 
                        count+=1
        
            print("Length of new_psl_entries_list: " + str(len(psl_object_list)) + " Identified Entries: " + str(count))
            assert(count == len(TSL_game_list_to_be_added))
            print("PSL entries generated: " + ', '.join(new_psl_entries_list))
