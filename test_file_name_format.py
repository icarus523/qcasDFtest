import os
from test_datafiles import QCASTestClient, PSLfile

class test_file_name_format(QCASTestClient): 

    def test_PSLfile_ends_with_PSL(self):
        assert(str(self.PSLfile).upper().endswith("PSL"))
        #self.assertEqual(str(self.PSLfile), "psl")

    def test_MSLfile_ends_with_MSL(self):
        assert(str(self.MSLfile).upper().endswith("MSL"))

    def test_TSLfile_ends_with_TSL(self):
        assert(str(self.TSLfile).upper().endswith("TSL"))

    def test_PSL_file_version_increment(self):
        psl_version = self.get_filename_version(self.PSLfile)
        next_month_psl_version = self.get_filename_version(self.nextMonth_PSLfile)

        # if month is the same, version should increment
        current_month = self.get_filename_month(self.PSLfile)
        next_month = self.get_filename_month(self.nextMonth_PSLfile)

        if current_month == next_month: 
            self.assertNotEqual(next_month_psl_version, psl_version)
        else:
            self.assertEqual(next_month_psl_version, '01')
                             
        
    def test_PSL_filename_date(self):
        current_month = self.get_filename_month(self.PSLfile)
        next_month = self.get_filename_month(self.nextMonth_PSLfile)

        current_month_year = self.get_filename_year(self.PSLfile)
        next_month_year = self.get_filename_year(self.nextMonth_PSLfile)

        
        
