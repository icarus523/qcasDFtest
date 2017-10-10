import os
from test_datafiles import QCASTestClient, PSLfile

class test_file_format(QCASTestClient):

    def test_PSLfile_ends_with_PSL(self):
        assert(str(self.PSLfile).endswith("psl"))
        #self.assertEqual(str(self.PSLfile), "psl")

    def test_MSLfile_ends_with_MSL(self):
        assert(str(self.MSLfile).endswith("msl"))

    def test_TSLfile_ends_with_TSL(self):
        assert(str(self.TSLfile).endswith("tsl"))

    def test_Read_PSL_file(self):
        assert(os.path.isfile(self.PSLfile) == True)

    def test_Read_TSL_file(self):
        assert(os.path.isfile(self.TSLfile) == True)

    def test_Read_MSL_file(self):
        assert(os.path.isfile(self.MSLfile) == True)

    def test_MSL_file_one_row(self):
        with open(self.MSLfile, 'r') as msl:
            assert(sum(1 for _ in msl) == 1) # count the number of rows

    def test_MSL_fields(self):
        # Check for MSL file format
        msl_file = self.check_file_format(self.MSLfile, 'MSL')

        # Test the year is this month's or next
        assert(self.check_month_field(msl_file.month) == True)

        # Test the year is this year's or next. 
        assert(self.check_year_field(msl_file.year) == True)

    def test_PSL_fields(self):

        # Check for PSL File Format
        game_list = self.check_file_format(self.PSLfile, 'PSL')

        for game in game_list:
            # Check for PSL manufacturer field
            assert(self.check_manufacturer(game.manufacturer) == True, "MID Invalid")

            # Check for PSL Game name field
            assert(self.check_game_name(game.game_name) == True, "Game Name empty")

            # Check for PSL year field

            # Check for PSL month field

            # Check Hash List for each day of the month, with the seed. 
            assert(self.check_hash_list(game.hash_list) == True, "Hashlist incorrect")
    
