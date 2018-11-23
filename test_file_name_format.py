import os
import unittest
from test_datafiles import QCASTestClient, PSLfile, skipping_PSL_comparison_tests

class test_file_name_format(QCASTestClient): 

    def test_MSL_filename_ends_with_MSL(self):
        assert(str(self.MSLfile).upper().endswith("MSL"))
        
        if not skipping_PSL_comparison_tests(): # Do Assert only for Both Months
            assert(str(self.nextMonth_MSLfile).upper().endswith("MSL"))

    def test_MSL_filename_date(self):
        current_month = self.get_filename_month(self.MSLfile)
        # year is to be same, unless current month = 12 (Dec)
        current_month_year = self.get_filename_year(self.MSLfile)
        
        if not skipping_PSL_comparison_tests():
            next_month = self.get_filename_month(self.nextMonth_MSLfile)

            # current month != next month
            self.assertNotEqual(current_month, next_month, msg="MSL files are the same")

            next_month_year = self.get_filename_year(self.nextMonth_MSLfile)

            if int(current_month) < 12 :
                self.assertEqual(int(next_month_year), int(current_month_year)) # same year

            if int(next_month) == 12:
                self.assertNotEqual(int(current_month_year), int(next_month_year) + 1) # new year

            if self.is_new_year(self.MSLfile):
                self.assertEqual(int(next_month_year), 1)

    def test_MSL_filename_version(self):
        version = self.get_filename_version(self.MSLfile)
        self.assertEqual(int(version), 1) # version must always be v1.
        
        if not skipping_PSL_comparison_tests():
            nextmonth_version = self.get_filename_version(self.nextMonth_MSLfile)
            self.assertEqual(int(nextmonth_version), 1) # version must always be v1.

    def test_TSLfile_ends_with_TSL(self):
        assert(str(self.TSLfile).upper().endswith("TSL")) # only 1 TSL file

    ### PSL file name format tests
    def test_PSLfile_ends_with_PSL(self):
        assert(str(self.PSLfile).upper().endswith("PSL"))
        
        if not skipping_PSL_comparison_tests():
            assert(str(self.nextMonth_PSLfile).upper().endswith("PSL"))
    
    ## @unittest.skip("Skipping PSL version inc tests")        
    def test_PSL_file_version_increment(self):
        psl_version = self.get_filename_version(self.PSLfile)
        current_month = self.get_filename_month(self.PSLfile)
        
        if not skipping_PSL_comparison_tests():
            next_month_psl_version = self.get_filename_version(self.nextMonth_PSLfile)
            next_month = self.get_filename_month(self.nextMonth_PSLfile)

        
        # "PSLfile": "G:\\OLGR-TECHSERV\\MISC\\BINIMAGE\\qcas\\qcas_2018_07_v04.psl",
        # "nextMonth_PSLfile": "G:\\OLGR-TECHSERV\\MISC\\BINIMAGE\\qcas\\qcas_2018_08_v02.psl",

        # if month is the same, version should increment
        # This is the only thing we can reliably test. 
            if current_month == next_month:
                # next month version should always be greater than current month
                self.assertTrue(int(next_month_psl_version) > int(psl_version))
        # else:
            # # Months are not equal, therefore versions can be anything
            # # without knowing what the previous current month file was 
            # # can't assume that the next month psl version is equal to 1.

            # # Assume the previous PSL file and previous nextMonthPSL file
            # previous_PSLfile = "qcas_" + self.get_filename_year(self.PSLfile) + "_" + current_month + "_v" + self.format_twoDigit(int(psl_version) - 1) + ".psl"
            # previous_nextMonth_PSLfile = "qcas_" + self.get_filename_year(self.nextMonth_PSLfile) + "_" + next_month + "_v" + self.format_twoDigit(int(next_month_psl_version) - 1) + ".psl"
            # path = os.path.dirname(self.PSLfile)
            # previous_PSLfile = os.path.join(path, previous_PSLfile)
            # previous_nextMonth_PSLfile = os.path.join(path, previous_nextMonth_PSLfile)
            
            # test these files exists, if they exist then the format of the files they were derived from (PSLfile and nextMonth PSLfile) is correct
            # self.assertTrue(os.path.isfile(previous_PSLfile))
            # self.assertTrue(os.path.isfile(previous_nextMonth_PSLfile))
            
            # # Additional Validations for the assumed PSL files: 
            # # Parse the PSL files
            # pslfile_list = [previous_PSLfile, previous_nextMonth_PSLfile] # test both months

            # for pslfile in pslfile_list: 
            # # Check for PSL File Format by Instantiating an object of PSL type
                # game_list = self.check_file_format(pslfile, 'PSL')

                # for game in game_list:
                    # # Check for PSL manufacturer field
                    # self.assertTrue(self.check_manufacturer(game.manufacturer))

                    # # Check for PSL Game name field
                    # self.assertTrue(self.check_game_name(game.game_name))

                    # # Check for PSL year field
                    # self.assertTrue(self.check_year_field(game.year))
                    
                    # # Check for PSL month field
                    # self.assertTrue(self.check_month_field(game.month))
            
        #else: 
        #    self.assertEqual(int(next_month_psl_version), 1) # New Month, version is v1                           
        
    def test_PSL_filename_date(self):
        current_month = self.get_filename_month(self.PSLfile)
        current_month_year = self.get_filename_year(self.PSLfile)
        
        if not skipping_PSL_comparison_tests():
            next_month = self.get_filename_month(self.nextMonth_PSLfile)

            # current month != next month
            self.assertNotEqual(current_month, next_month, msg="PSL files are the same")

            # year is to be same, unless current month = 12 (Dec)
            next_month_year = self.get_filename_year(self.nextMonth_PSLfile)

            if int(current_month) < 12 :
                self.assertEqual(int(next_month_year), int(current_month_year), 
                    msg="current PSL Month is less than December, expect same year" ) # same year

            if int(next_month) == 12:
                self.assertNotEqual(int(current_month_year), int(next_month_year) + 1) # new year
        
