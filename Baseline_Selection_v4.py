#!/usr/bin/env python
# coding: utf-8

# In[1]:


import uproot as up
import awkward as ak
import numpy as np
import argparse

# In[2]:


import glob


# In[3]:

parser = argparse.ArgumentParser()
parser.add_argument('input',action='store',type=str,help='input file name')
parser.add_argument('-o','--output',action='store',type=str,help='output file name')
args = parser.parse_args()

#경로상의 모든 root파일 가져오기
#file_list = glob.glob("*.root")
#print(len(file_list)," files to do")


# In[4]:


# Baseline Selection 에 필요한 variables 가져오기
def get_var(tree):
	jet_pt = tree['JetPUPPI/JetPUPPI.PT'].array()
	jet_eta = tree['JetPUPPI/JetPUPPI.Eta'].array()
	jet_btag = tree['JetPUPPI/JetPUPPI.BTag'].array()
	return jet_pt,jet_eta,jet_btag


# In[5]:


#Baseline Selection 통과한 event의 index 가져오기
def get_pass_BS(tree):
	selEvents=[]
	jet_pt, jet_eta, jet_btag = get_var(tree)
	nEvents = len(jet_pt)
	for ievt in range(0,nEvents):
		selJets = (jet_pt[ievt]>30) & (np.fabs(jet_eta[ievt])<2.4)
		if np.sum(selJets) < 5 : continue
		selBjets = (jet_btag[ievt][selJets]>30)
		if np.sum(selBjets)<1:continue
		selEvents.append(ievt)
	return selEvents


# In[6]:


n_do = 0
infile = args.input
print("Processing ",infile)
f = up.open(infile)
tree = f['Delphes']
selE = get_pass_BS(tree)
print("Number of Selected Events : ",len(selE))

#Get Track , Tower , MET pt eta phi for selected Events
sel_tracks = ak.zip({
	"PT"  : tree['Track/Track.PT'].array()[selE],
	"Eta" : tree['Track/Track.Eta'].array()[selE],
	"Phi" : tree['Track/Track.Phi'].array()[selE]
})

sel_towers = ak.zip({
	"Eta"  :tree['Tower/Tower.Eta'].array()[selE],
	"Phi"  :tree['Tower/Tower.Phi'].array()[selE],
	"Eem"  :tree['Tower/Tower.Eem'].array()[selE],
	"Ehad" :tree['Tower/Tower.Ehad'].array()[selE]
})
	#Save to npy file
	#Selected info to dictionary
out={}
out['sel_event_idx'] = selE
out['sel_tracks']=sel_tracks
out['sel_towers']=sel_towers
	#make npy file
out_name = args.output+'_selected.npy'
np.save(out_name,out)
print(out_name," saved!")
