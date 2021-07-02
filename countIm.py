import h5py as h5
import glob

file_list = glob.glob("*.h5")

count = 0
for infile in file_list:
	f = h5.File(infile,'r')
	nEvt = len(f['all_events/images'])
	count += nEvt

print(count)
