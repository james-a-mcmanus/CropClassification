import os

def lines_from_file(textfile):
	with open(textfile) as f:
		return f.readlines(f)

def compare_directories(complete_files, drive_files):
	missing_files = []
	for file in complete_files:
		if not os.path.isfile(file):
			missing_files.append(file)
	return missing_files

