import os

def lines_from_file(textfile):
	"""
	textfile: path of a file containing set of lines. (e.g. filenames)

	returns: list of lines from that file
	"""
	with open(textfile) as f:
		filelist = f.readlines()
	return [file.rstrip() for file in filelist]



def compare_directories(complete_files, drive_files):
	"""
	complete_files: list of complete filenames
	drive_files: list of files in another directory

	returns: the number of missing files
	"""
	missing_files = []
	for file in complete_files:
		if file not in drive_files:
			missing_files.append(file)
	return missing_files

