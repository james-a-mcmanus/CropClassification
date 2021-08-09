import os

def lines_from_file(textfile):
	with open(textfile) as f:
		filelist = f.readlines()
	return [file.rstrip() for file in filelist]

def compare_directories(complete_files, drive_files):
	missing_files = []
	for file in complete_files:
		if file not in drive_files:
			missing_files.append(file)
	return missing_files

