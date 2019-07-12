"""
Reads .db files produced by ChangeAbsPositionAz.tnhs script
Counts hits on absorber for each angle and position
Plots heatmap
Plots yposition - angle linear regression
"""

import os
import glob
import sqlite3
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from statsmodels.api import add_constant


def view(dbname):
    """ Reads .db files
    :param str dbname: .db file path
    :returns: contents of Photons and Surfaces tables
    """
    conn = sqlite3.connect(dbname)
    df = pd.read_sql_query("SELECT * FROM Photons", con=conn)
    ids = pd.read_sql_query("SELECT * FROM Surfaces", con=conn)
    conn.close()
    return df, ids


def load(dbfiles):
    """ Counts hits on absorber and mirror aperture (auxiliary surface) and calculates intercept factor

    :param list dbfiles: list of .dbfiles
    :returns: dataframe with intercept factor for each position and angle
    """
    df = pd.DataFrame(columns=['angle', 'position', 'intercept factor'])
    for i in dbfiles:
        fname = os.path.basename(i).split('_')
        pos = fname[0]  # extracts abs position from filename
        angle = fname[1][:-3]  # extract angle from filename
        pos = float(pos) * 1000  # converts abs position to mm
        photons, surfaces = view(i)
        aux_id = surfaces['id'][surfaces["Path"].str.contains("aux_surface")].values[0]  # Finds auxiliary surface id
        aux_hits = photons['surfaceID'].value_counts()[aux_id]
        try:
            absorber_id = surfaces['id'][surfaces["Path"].str.contains("Tracking_unit")].values[0]  # Finds absorber id
            abs_hits = photons['surfaceID'].value_counts()[absorber_id]
            nj = 100*abs_hits/aux_hits
            df = df.append({'angle': angle, 'position': pos, 'intercept factor': nj},
                             ignore_index=True)
        except IndexError:
            print('No absorber surface in:', os.path.basename(i), 'skipping...')
            pass
    df = df.astype(int)
    df = df.pivot('position', 'angle', 'intercept factor')
    df = df.sort_values(by='position', ascending=False)
    return df

def get_maxnj(df):
    """ 
    Selects max intercept factor values for each azimuth angle
    :param df: pd.DataFrame
    :return: pd.DataFrame
    """
    dfnj = pd.DataFrame(columns=['angle','pos','maxnj'])
    angles = list(df)
    for j in angles:
        max_nj = df[j].nlargest(1).values[0]
        bestpos = df[j].nlargest(1).index.values[0]
        dfnj = dfnj.append({'angle':j,'pos':bestpos, 'maxnj': max_nj},ignore_index=True)
    dfnj = dfnj.set_index('angle',drop=True)
    return dfnj

def linregres(df):
    """ Calculates linear regression parameters and standard errors"""
    x = df.index.values
    y = df['pos'].values.tolist()

    X = add_constant(x)  # include constant (intercept) in ols model
    mod = sm.OLS(y, X)
    results = mod.fit()
    #    intercept, slope = results.params
    #    intercept_stderr, slope_stderr = results.bse
    #    rsquared = results.rsquared
    return results

def linear_fit(df,picname = None):
    """ Plots Y-angle scatter, line and equation
    If picname specified, saves plot"""
    x = df.index.values
    y = df['pos'].values.tolist()
    res = linregres(df)
    intercept,slope = res.params

    fig, axes = plt.subplots()
    axes = sns.regplot(x = x, y=y, line_kws={'label': f"$y={slope:.4f}x{intercept:+.4f}$"})
    axes.legend()
    axes.set_ylabel('Y (m)')
    axes.set_xlabel(r'$\theta_{az} (°)$')
    plt.show()
    try:
        fig.savefig(picname)
    except:
        pass


def linregres2csv(df,csvname=None):
    """ Prints linear regression parameters and standard errors
    If csvname specified, saves dataframe to .csv"""
    linres = linregres(df)
    rdf = pd.DataFrame(columns=['Intercept','Slope'])
    rdf.loc['Value']= linres.params[:] # Fill rows
    rdf.loc['SE']= linres.bse[:]
    rdf.loc['StDev'] = linres.bse*np.sqrt(linres.nobs)
    rdf.loc['R2'] = linres.rsquared
    rdf.loc['n'] = linres.nobs
    rdf.loc['P-value'] = linres.pvalues[:]
    rdf = rdf.T # Transpose
    rdf.index.name='Parameter'
    print(rdf)
    try:
        rdf.to_csv(csvname,float_format='%g')
    except:
        pass

def make_dir(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)
    return f"{os.getcwd()}/{dirname}/"

dbfileslist = glob.glob(os.getcwd() + '/raw/*.db') # creates list of .db files in /raw
dfr = load(dbfileslist)

ax = sns.heatmap(dfr,cbar_kws={'label': '$\gamma_{th}$'})

maxnj = get_maxnj(dfr)
maxnj['pos'] = maxnj['pos']/1000 # converts to m

dfleft = maxnj.loc[:180] # selects angles up to 180°
dfright = maxnj.loc[181:] # selects angles over 180°


linear_fit(dfleft,picname=make_dir('results/plots')+'linregres_left.png')
linear_fit(dfright,picname=make_dir('results/plots')+'linregres_right.png')
linregres2csv(dfleft,csvname=make_dir('results')+'regresults_left.csv')
linregres2csv(dfright,csvname=make_dir('results')+'regresults_right.csv')

