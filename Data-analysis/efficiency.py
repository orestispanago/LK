import os
import glob
import pandas as pd


cwd = os.getcwd()
outdir = cwd + '/output/'
if not os.path.exists(outdir):
    os.makedirs(outdir)
csvfiles = glob.glob(cwd + '/raw/*.csv')
csvfiles.sort(key=lambda x: int(os.path.split(x)[1][:-4]))


df = pd.read_csv(csvfiles[0])
angle = int(os.path.split(csvfiles[0])[1][:-4])

abs_hits = df['element'][df['element']==-4].value_counts().sum()
ref_hits = df['element'][df['element']==1].value_counts().sum()
efficiency = abs_hits/ref_hits

out = df['element'][df['element']==-1].value_counts().sum()