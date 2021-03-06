import os, glob
import numpy as np
import pandas as pd
import streamlit as st

rulefolder = 'rules'


@st.cache
def get_csvdf(rulefolder):
    files2 = glob.glob(rulefolder + '**/*.csv', recursive=True)
    dflist = []
    for filepath in files2:
        basename = os.path.basename(filepath)
        filename = os.path.splitext(basename)[0]
        newdf = rule2df(filename, filepath)[['监管要求', '结构', '条款']]
        dflist.append(newdf)
    alldf = pd.concat(dflist, axis=0)
    return alldf


def rule2df(filename, filepath):
    docdf = pd.read_csv(filepath)
    docdf['监管要求'] = filename
    return docdf


def get_embedding(folder, emblist):
    dflist = []
    for file in emblist:
        filepath = os.path.join(folder, file + '.npy')
        embeddings = np.load(filepath)
        dflist.append(embeddings)
    alldf = np.concatenate(dflist)
    return alldf


# split string by space into words, add brackets before and after words, combine into text
def split_words(text):
    words = text.split()
    words = ['(?=.*' + word + ')' for word in words]
    new = ''.join(words)
    return new


# get section list from df
def get_section_list(searchresult, make_choice):
    '''
    get section list from df
    
    args: searchresult, make_choice
    return: section_list
    '''
    df = searchresult[(searchresult['监管要求'].isin(make_choice))]
    conls = df['结构'].drop_duplicates().tolist()
    unils = []
    for con in conls:
        itemls = con.split('/')
        for item in itemls[:2]:
            unils.append(item)
    # drop duplicates and keep list order
    section_list = list(dict.fromkeys(unils))
    return section_list


# get folder name list from path
def get_folder_list(path):
    folder_list = [
        folder for folder in os.listdir(path)
        if os.path.isdir(os.path.join(path, folder))
    ]
    return folder_list


def get_rulefolder(industry_choice):
    # join folder with industry_choice
    folder = os.path.join(rulefolder, industry_choice)
    return folder
