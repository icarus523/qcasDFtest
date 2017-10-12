import os
from test_datafiles import QCASTestClient, PSLfile

class test_file_name_format(QCASTestClient): 

    def test_MSL_filename_ends_with_MSL(self):
        assert(str(self.MSLfile).upper().endswith("MSL"))
        assert(str(self.nextMonth_MSLfile).upper().endswith("MSL"))

    def test_MSL_filename_date(self):
        current_month = self.get_filename_month(self.MSLfile)
        next_month = self.get_filename_month(self.nextMonth_MSLfile)

        # current month != next month
        self.assertNotEqual(current_month, next_month)

        # year is to be same, unless current month = 12 (Dec)
        current_month_year = self.get_filename_year(self.MSLfile)
        next_month_year = self.get_filename_year(self.nextMonth_MSLfile)

        if int(current_month) < 12 :
            self.assertEqual(int(next_month_year), int(current_month_year)) # same year

        if int(next_month) == 12:
            self.assertNotEqual(int(current_month_year), int(next_month_year) + 1) # new year

        if self.is_new_year(self.MSLfile):
            self.assertEqual(int(next_month_year), 1)


    def test_MSL_filename_version(self):
        version = self.get_filename_version(self.MSLfile)
        nextmonth_version = self.get_filename_version(self.nextMonth_MSLfile)

        # version must always be v1.
        self.assertEqual(int(version), 1)
        self.assertEqual(int(nextmonth_version), 1)

    def test_TSLfile_ends_with_TSL(self):
        assert(str(self.TSLfile).upper().endswith("TSL")) # only 1 TSL file

    ### PSL file name format tests
    def test_PSLfile_ends_with_PSL(self):
        assert(str(self.PSLfile).upper().endswith("PSL"))
        assert(str(self.nextMonth_PSLfile).upper().endswith("PSL"))

    def test_PSL_file_version_increment(self):
        psl_version = self.get_filename_version(self.PSLfile)
        next_month_psl_version = self.get_filename_version(self.nextMonth_PSLfile)

        # if month is the same, version should increment
        current_month = self.get_filename_month(self.PSLfile)
        next_month = self.get_filename_month(self.nextMonth_PSLfile)

        #if self.is_new_month(self.PSLfile, self.nextMonth_PSLfile):
        #    self.assertEqual(int(next_month_psl_version), 1) # New Month, version is v1                           
        #else:
             # next month version should always be greater than current month, unless it's a new month
        #    self.assertTrue(int(next_month_psl_version) > int(psl_version))

        
    def test_PSL_filename_date(self):
        current_month = self.get_filename_month(self.PSLfile)
        next_month = self.get_filename_month(self.nextMonth_PSLfile)

        # current month != next month
        self.assertNotEqual(current_month, next_month)

        # year is to be same, unless current month = 12 (Dec)
        current_month_year = self.get_filename_year(self.PSLfile)
        next_month_year = self.get_filename_year(self.nextMonth_PSLfile)

        if int(current_month) < 12 :
            self.assertEqual(int(next_month_year), int(current_month_year)) # same year

        if int(next_month) == 12:
            self.assertNotEqual(int(current_month_year), int(next_month_year) + 1) # new year
        
