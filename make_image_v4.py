#!/usr/bin/env python
# coding: utf-8

# In[1]:


import numpy as np
import awkward as ak
import glob
import matplotlib.pyplot as plt
import h5py
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('input',action='store',type=str,help='input file name')
parser.add_argument('-o','--output',action='store',type=str,help='output file name')
args = parser.parse_args()

# In[2]:


#file_list = glob.glob("*.npy")
#print(len(file_list)," files to do")

infile = args.input

# In[3]:
#To sent the phi with the highes pt to the origin
def cent_phi(pt,phi):
	centered_arr = []
	for i in range(0,len(pt)):
		pt_a = pt[i]
		phi_a = phi[i]-phi[i][np.argmax(pt_a)]
		
		centered = []
		for j in phi_a :
			if j > np.pi:
				j = j - np.pi
				centered.append(j)
			elif j < -np.pi:
				j = j + np.pi
				centered.append(j)
			else:
				centered.append(j)
		centered_arr.append(centered)
	return centered_arr

# x-axis : eta , y-axis : phi , z-axis : pt
def getimage(pt,eta,phi):
	hs=[]
	rnge=((-2.4,2.4),(-np.pi,np.pi))
	
	for i in range(len(eta)):
		h=np.histogram2d(ak.to_numpy(eta[i]),ak.to_numpy(phi[i]),weights=ak.to_numpy(pt[i]),bins=224,range=rnge)
		hs.append(h[0])
	return np.stack(hs)


# In[4]:

	
dic=np.load(infile,allow_pickle=True)[()]
	   
#tracker hist
t_pt=dic['sel_tracks'].PT
t_eta=dic['sel_tracks'].Eta
t_phi=dic['sel_tracks'].Phi
t_im=getimage(t_pt,t_eta,t_phi)

#ECAL hist
e_pt=dic['sel_towers'].Eem
e_eta=dic['sel_towers'].Eta
e_phi=dic['sel_towers'].Phi
e_im=getimage(e_pt,e_eta,e_phi)

#HCAL hist
h_pt=dic['sel_towers'].Ehad
h_eta=dic['sel_towers'].Eta
h_phi=dic['sel_towers'].Phi
h_im=getimage(h_pt,h_eta,h_phi)

#merge HCAL, ECAL Tracker images
#for pytorch axis =1 , for tensorflow axis=-1
ax = 1
t_im = np.expand_dims(t_im,ax)
e_im = np.expand_dims(e_im,ax)
h_im = np.expand_dims(h_im,ax)
images = np.concatenate([t_im,e_im,h_im],axis=ax)

#Save images to h5 files
out_name = args.output+'.h5'
with h5py.File(out_name,'w',libver='latest',swmr='True') as outFile:
	g = outFile.create_group('all_events')
	g.create_dataset('weights',data=np.ones(len(images)),dtype='f4')
	g.create_dataset('images',data=images)


