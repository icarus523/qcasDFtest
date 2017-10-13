import os
import csv

from test_datafiles import QCASTestClient, PSLfile, TSLfile

class test_chk01_checklist(QCASTestClient):
   
    def test_Generated_PSL_files_Differ(self):
        same = set()
        
        with open(self.PSLfile, 'r') as file1:
            with open(self.nextMonth_PSLfile, 'r') as file2:
                same = set(file1).intersection(file2)
   
        self.assertFalse(len(same) > 0)
                
    def test_new_games_to_be_added_are_in_PSL_files(self):
        tsl_difference = set()
        game_list_to_be_added = list()
        
        with open(self.TSLfile, 'r') as file1:
            with open(self.previous_TSLfile, 'r') as file2:
                tsl_difference = set(file1).difference(file2)
        
        self.assertTrue(len(tsl_difference) > 0) # TSL files must be contain a new game? 
        print("\nNew Games added: \n" + "".join(list(tsl_difference)))
  
        # Differences are the new games to be added. 
        for game in list(tsl_difference): # Single Line
            game_list_to_be_added.append(TSLfile(game)) # Generate TSL object
            
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
            for tslitem in psl_difference: 
                print("Verified added games in " + psl_file + " is: " + tslitem.game_name)
                
            self.assertTrue(set(verified_game).intersection(set(game_list_to_be_added)))
             