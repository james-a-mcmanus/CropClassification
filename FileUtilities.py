import os, json, rasterio
import matplotlib.pyplot as plt
import numpy as np

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

def getbyextension(filelist, extension):
	return [fname for fname in filelist if os.path.splitext(fname)[1] == extension]


class AbstractLoader(object):
	def __init__(self, filepath):
		self.path = filepath
		self.subfiles = os.listdir(filepath)
		self.tif_paths=getbyextension(self.subfiles, '.tif')
		self.load_json()

	def load_json(self):
		jsonpath = getbyextension(self.subfiles, '.json')
		if len(jsonpath) == 1:
			self.jsonpath = os.path.join(self.path, jsonpath[0])
		else:
			raise Exception(f'There seems to be {len(jsonpath)} .json files at that location')
		with open(self.jsonpath, 'r') as f:
			self.metadata = json.load(f)

class Sentinel2(AbstractLoader):
	"""
	Sentobject for loading in the S2 data.
	filepath: path to the directory containing the .tif and json files.
	"""
	def __init__(self, filepath):
		super().__init__(filepath)
		self.bands = self.get_bands()
		self.tifs = None
		self.load_all_tifs()

	def get_bands(self):
		bandprops = self.metadata['properties']['eo:bands']
		return [prop['name'] for prop in bandprops]
	
	def load_all_tifs(self):
		tifdict = {}
		for bandname in self.bands:
			tifdict[bandname] = self.load_tif(bandname)
		self.tifs = tifdict

	def load_tif(self, bandname):
		tifname = os.path.join(self.path, self.metadata['assets'][bandname]['href'])
		tif = rasterio.open(tifname)
		return tif.read().squeeze(0)

	def plot_band(self, bandname, ax=None):
		if ax:
			return ax.imshow(self.tifs[bandname])
		else:
			plt.imshow(self.tifs[bandname])
			plt.show()

	def plot_tif(self, tif, ax=None):
		if ax:
			return ax.imshow(tif)
		else:
			plt.imshow(tif)
			plt.show()

class Label(AbstractLoader):
	def __init__(self, filepath):
		super().__init__(filepath)
		

