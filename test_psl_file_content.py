from test_datafiles import QCASTestClient, PSLfile

class test_PSLfile_content(QCASTestClient): 
    
    # Verify that valid MIDs have PSL entries. 
    def test_valid_MIDs_have_PSL_entries(self): 
        verified_manufacturer = list()
        pslfile_list = [self.PSLfile, self.nextMonth_PSLfile] # test both months
        
        for pslfile in pslfile_list: 
            # Check for PSL File Format by Instantiating an object of PSL type
            game_list = self.check_file_format(pslfile, 'PSL')
            
            for game in game_list:
                if game.manufacturer in self.my_preferences.mid_list:
                    verified_manufacturer.append(game.manufacturer)
            
            sorted_verified_mid = list() # need to sort list in this way
            for mid in sorted(list(set(verified_manufacturer))): 
                sorted_verified_mid.append(mid)
            
            #if sorted_verified_mid.sort() == self.manufacturer_id_list.sort(): 
            #   print("verified_manufacturer.sort(): " + ",".join(sorted_verified_mid))
            #   print("self.manufacturer_id_list.sort(): " + ",".join(self.manufacturer_id_list))
            
            self.assertTrue(sorted_verified_mid, self.my_preferences.mid_list.sort())
                  
    
    def test_date_field_in_PSL_entry_equals_date_field_in_filename(self): 
        pslfile_list = [self.PSLfile, self.nextMonth_PSLfile] # test both months
        psl_field_month = ''
        psl_field_year = ''
        
        for pslfile in pslfile_list: 
            first_line = True # reset flag for each pslfile
            game_list = self.check_file_format(pslfile, 'PSL')
            
            for game in game_list: 
                if first_line: # first entry, save current year & month
                    psl_field_month = game.month
                    psl_field_year = game.year
                    first_line = False
                
                # validate the month/year field in each PSL entry are the same.
                self.assertEqual(game.month, psl_field_month)
                self.assertEqual(game.year, psl_field_year)

                # Check Month PSL field matches filename
                self.assertEqual(int(game.month), int(self.get_filename_month(pslfile)))
                
                # Check Year PSL field matches filename
                self.assertEqual(int(game.year), int(self.get_filename_year(pslfile)))

        
        