# Clean folder

This package processing each file based on the folder: 
renaming - by the normalize function
create folder by dictionary key if missing
moving the file to this folder, adding it to the list of known extensions depending on the dictionary key
for archives: create folder by dictionary key, create subfolder by archive name, unpack archive into subfolder
for unknown - create a list of unknown extensions 