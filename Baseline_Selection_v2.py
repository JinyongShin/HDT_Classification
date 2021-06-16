#!/usr/bin/env python
# coding: utf-8

# In[1]:


import uproot as up
import awkward as ak
import numpy as np


# In[2]:


import glob


# In[3]:


#경로상의 모든 root파일 가져오기
file_list = glob.glob("*.root")
print(len(file_list)," files to do")


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
        selBjets = (jet_btag[ievt][selJets]>0.5)
        if np.sum(selBjets)<1:continue
        selEvents.append(ievt)
    return selEvents


# In[6]:


n_do = 0
for infile in file_list:
    print("Processing ",infile)
    f = up.open(infile)
    if 'Delphes' not in f : continue
    tree = f['Delphes']
    if tree == None : continue
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
    sel_MET = ak.zip({
        "MET" : tree['PuppiMissingET/PuppiMissingET.MET'].array()[selE],
        "Eta" : tree['PuppiMissingET/PuppiMissingET.Eta'].array()[selE],
        "Phi" : tree['PuppiMissingET/PuppiMissingET.Phi'].array()[selE]
    })
    
    #Save to npy file
    #Selected info to dictionary
    out={}
    out['sel_tracks']=sel_tracks
    out['sel_towers']=sel_towers
    out['sel_MET']=sel_MET
    #make npy file
    out_name = infile.split(".")[0]+'_selected.npy'
    np.save(out_name,out)
    print(out_name," saved!")
    n_do += 1
    print(n_do , " of ", len(file_list)," is done")

