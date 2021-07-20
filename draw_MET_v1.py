import numpy as np
import argparse
import yaml
import glob
import uproot as up
from tqdm import tqdm
import matplotlib.pyplot as plt
import awkward as ak

parser = argparse.ArgumentParser()
parser.add_argument('-c','--config',action='store',type=str,default='config.yaml',help='Config file with sample information')
parser.add_argument('-o',action='store',type=str,required=True,help='Output file name without .png')
parser.add_argument('-l','--lumi',action='store',type=int,default='3000000',help='luminosity (pb)')

args = parser.parse_args()

lumi = args.lumi

config = yaml.load(open(args.config).read(),Loader=yaml.FullLoader)

MyData=[]

print('Reading your config file')

for sampleInfo in tqdm(config['samples']):
	name = sampleInfo['name']
	root_path = sampleInfo['path']+'*.root'
	npy_path = sampleInfo['path']+'condorBaseOut/*.npy'
	weight=lumi*sampleInfo['xsec']/sampleInfo['ngen']
	A = [name,root_path,npy_path,weight]
	MyData.append(A)
print('Done')

### From root file path to sorted list for uproot4 input
def up4_list(rpath):
	f_list = glob.glob(rpath)
	f_list = sorted(f_list)
	new_list = []
	for f in f_list:
		new_list.append(f+':Delphes')
	return new_list

### From list made by up4_list function, get MET
def get_MET(rflist):
	branches = ['PuppiMissingET.MET']
	print('Reading ',branches,' from your root files')
	MET=[]
	for arrays in tqdm(up.iterate(rflist,branches)):
		f_MET=arrays[b"PuppiMissingET.MET"]
		MET.append(f_MET)
	print('Done')
	return MET

### From ntuples which have ['sel_event_idx'] get number of event that passed baseline selection
def get_sel_idx(nflist):
	idx = []
	for nf in tqdm(nflist):
		dic = np.load(nf,allow_pickle=True)[()]
		sel_idx = dic['sel_event_idx']
		idx.append(sel_idx)
	return idx


hist_list = []
label_list = []
weight_list = []
for name,rpath,npath,weight in MyData:

	print(name)

	hist1=[]
	weight_arr=[]
	MET=[]
	idx=[]

	name2 = name.replace(" ","")
	globals()[name2]=[]

	rflist = up4_list(rpath)
	nflist = glob.glob(npath)
	nflist = sorted(nflist)

	MET = get_MET(rflist)
	idx = get_sel_idx(nflist)
	print(len(MET),len(idx))

	sel_MET = []
	for i in range(0,len(MET)):
		sel_MET = MET[i][idx[i]]
		globals()[name2].append(sel_MET)

	hist1 = np.concatenate(globals()[name2])
	hist1 = ak.flatten(hist1)
	hist1 = ak.to_numpy(hist1)

	weight_arr = np.ones(len(hist1))*weight

	hist_list.append(hist1)
	weight_list.append(weight_arr)
	label_list.append(name)

label_list = ak.to_numpy(label_list)
print(label_list)

hist_list = ak.to_numpy(hist_list)
print(hist_list)

weight_list = ak.to_numpy(weight_list)
print(weight_list)
plt.hist(hist_list,weights=weight_list,label=label_list,range=(0,1000),bins=20,stacked=True)
#plt.hist(hist_list,weights=weight_list,range=(0,1000),bins=20)
plt.yscale('log')
plt.legend()
plt.savefig('test_1.png')
