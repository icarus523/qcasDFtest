from test_datafiles import Preferences

my_pref = Preferences()

my_pref.scan_datafiles()

print(",".join(my_pref.psl_file_list)) 
print(",".join(my_pref.msl_file_list)) 
print(",".join(my_pref.tsl_file_list)) 

