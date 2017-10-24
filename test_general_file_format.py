import os
from test_datafiles import QCASTestClient, PSLfile

class test_general_file_format(QCASTestClient):
   
    def test_Read_PSL_file(self):
        self.assertTrue(os.path.isfile(self.PSLfile))
        self.assertTrue(os.path.isfile(self.nextMonth_PSLfile))

    def test_Read_TSL_file(self):
        self.assertTrue(os.path.isfile(self.TSLfile))
        self.assertTrue(os.path.isfile(self.previous_TSLfile))
        
    def test_MSL_fields(self):
        mslfile_list = [self.MSLfile, self.nextMonth_MSLfile]

        for mslfile in mslfile_list: 
            # Check for MSL file format
            msl_file_list = self.check_file_format(self.MSLfile, 'MSL')

            if len(msl_file_list) == 1: # has to be one entry
                # Test the year is this month's or next
                self.assertTrue(self.check_month_field(msl_file_list[0].month))

                # Test the year is this year's or next.
                self.assertTrue(self.check_year_field(msl_file_list[0].year))

                # Test the number of seeds equal 31
                self.assertEqual(len(msl_file_list[0].seed_list), 31)
            else:
                self.assertNotEqual(len(msl_file_list), 1)

    def test_PSL_fields(self):
        pslfile_list = [self.PSLfile, self.nextMonth_PSLfile] # test both months

        for pslfile in pslfile_list: 
            # Check for PSL File Format by Instantiating an object of PSL type
            game_list = self.check_file_format(pslfile, 'PSL')

            for game in game_list:
                # Check for PSL manufacturer field
                self.assertTrue(self.check_manufacturer(game.manufacturer))

                # Check for PSL Game name field
                self.assertTrue(self.check_game_name(game.game_name))

                # Check for PSL year field
                self.assertTrue(self.check_year_field(game.year))
                
                # Check for PSL month field
                self.assertTrue(self.check_month_field(game.month))

                # Check Hash List for each day of the month, with the seed. 
                # Cannot check every game, as I can't verify PSA32 binimages. 
                # self.assertTrue(self.check_hash_list(game.hash_list))
    
    def test_TSL_fields(self):
        # only one TSL file
        tslfile_list = self.check_file_format(self.TSLfile, 'TSL')

        for tsl_entry in tslfile_list:
            # Check for TSL manufacturer field
            self.assertTrue(self.check_manufacturer(str(tsl_entry.mid)))

            # Check SSAN is unique
            self.assertTrue(self.check_unique_field(tsl_entry.ssan, tslfile_list, flag='SSAN'))

            # Check BNK File name is unique
            #@unittest.skipIf(tsl_entry.binfile == '0101230', "Duplicate entry exist for this game")

            # Check BNK Type is valid
            self.assertTrue(self.check_valid_binimage_type(tsl_entry.bin_type))