# coding: utf-8

import pandas as pd
import numpy as np
import os
import collections
import sys
import codecs
import jinja2
import copy
import csv
import datetime
import time


dir_path=os.path.dirname(os.path.abspath(__file__))
filename = dir_path + "\\Calendrier.csv"
#os.chdir(dname)


fsloader = jinja2.FileSystemLoader(dir_path) #dossier ou se trouve les template
env = jinja2.Environment(loader=fsloader)

df = pd.read_excel("Calendrier.xlsx")


dict_discipline = {'VTT': 'VTT', 'Route': 'route', 'Grimpée': 'grimpees', 'Randonnée': 'randonnees', 'Cyclo-cross' : "cyclo_cross"}

df = df.replace(np.nan, "", regex=True)


#df["lien_publi"] = "./" + df["Discipline"].map(dict_discipline) + "/publications/publication_" + df["FileName"] + ".pdf"
def j(a):
    return(a.startswith("http"))

df["lien_publi"] = np.where(df["FileName"].apply(j), df["FileName"] ,"./" + df["Discipline"].map(dict_discipline) + "/publications/publication_" + df["FileName"] + ".pdf")

df["lien_resul"] = "./" + df["Discipline"].map(dict_discipline) + "/resultats/resultats_" + df["FileName"] + ".pdf"

seconds = os.path.getmtime("./route/publications/Publication_Seppois.pdf")
a = datetime.datetime.strptime(time.ctime(seconds), "%a %b %d %H:%M:%S %Y").year

#df["publi_dispo"] = datetime.datetime.strptime(time.ctime(os.path.getmtime("Publication_Seppois.pdf")), "%a %b %d %H:%M:%S %Y").year == 2018
def f(x):
    return os.path.isfile(x)
def g(x):
    if f(x) == False:
        return 0
    return os.path.getmtime(x)


df["publi_dispo"] = False
df["resul_dispo"] = False

for i in range(len(df)):
    if j(df.iloc[i]['lien_publi']): #link
        df.iloc[i, df.columns.get_loc('publi_dispo')] = True

    if f(df.iloc[i]['lien_publi']) == True:
        df.iloc[i, df.columns.get_loc('publi_dispo')] = (   datetime.datetime.strptime(time.ctime(g(df.iloc[i]['lien_publi'])), "%a %b %d %H:%M:%S %Y").year == 2018    )
    if f(df.iloc[i]['lien_resul']) == True:
        df.iloc[i, df.columns.get_loc('resul_dispo')] = (   datetime.datetime.strptime(time.ctime(g(df.iloc[i]['lien_resul'])), "%a %b %d %H:%M:%S %Y").year == 2018    )


route_df = df[df["Discipline"] == "Route"]
vtt_df = df[df["Discipline"] == "VTT"]
cyclocross_df = df[df["Discipline"] == "Cyclo-cross"]
grimpees_df = df[df["Discipline"] == "Grimpée"]
rando_df = df[df["Discipline"] == "Randonnée"]

page="Accueil"
template = env.get_template('index.html.j2') #nomdutemplate
ofh = codecs.open("index.html","w", encoding="utf-8")
rt = template.render(page=page)
ofh.write(rt)
ofh.close()

page="Archives"
template = env.get_template('archives.html.j2') #nomdutemplate
ofh = codecs.open("archives.html","w", encoding="utf-8")
rt = template.render(page=page)
ofh.write(rt)
ofh.close()


page="Route"
template = env.get_template('route.html.j2') #nomdutemplate
ofh = codecs.open("route.html","w", encoding="utf-8")
rt = template.render(calendar = route_df, page=page)
ofh.write(rt)
ofh.close()

page="VTT"
template = env.get_template('vtt.html.j2') #nomdutemplate
ofh = codecs.open("vtt.html","w", encoding="utf-8")
rt = template.render(calendar = vtt_df, page=page)
ofh.write(rt)
ofh.close()

page="Cyclocross"
template = env.get_template('cyclocross.html.j2') #nomdutemplate
ofh = codecs.open("cyclocross.html","w", encoding="utf-8")
rt = template.render(calendar = cyclocross_df, page=page)
ofh.write(rt)
ofh.close()

page="Grimpees"
template = env.get_template('grimpees.html.j2') #nomdutemplate
ofh = codecs.open("grimpees.html","w", encoding="utf-8")
rt = template.render(calendar = grimpees_df, page=page)
ofh.write(rt)
ofh.close()

page="Randonnees"
template = env.get_template('randonnees.html.j2') #nomdutemplate
ofh = codecs.open("randonnees.html","w", encoding="utf-8")
rt = template.render(calendar = rando_df, page=page)
ofh.write(rt)
ofh.close()

page="Liens"
template = env.get_template('./liens/liens.html.j2') #nomdutemplate
ofh = codecs.open("./liens/liens.html","w", encoding="utf-8")
rt = template.render(calendar = rando_df, page=page)
ofh.write(rt)
ofh.close()

page="Documents"
template = env.get_template('./documents/documents.html.j2') #nomdutemplate
ofh = codecs.open("./documents/documents.html","w", encoding="utf-8")
rt = template.render(calendar = rando_df, page=page)
ofh.write(rt)
ofh.close()

page="CommissionAlsace"
template = env.get_template('./commission_alsace/commission_alsace.html.j2') #nomdutemplate
ofh = codecs.open("./commission_alsace/commission_alsace.html","w", encoding="utf-8")
rt = template.render(calendar = rando_df, page=page)
ofh.write(rt)
ofh.close()

page="Commissaires"
template = env.get_template('./commissaires/commissaires.html.j2') #nomdutemplate
ofh = codecs.open("./commissaires/commissaires.html","w", encoding="utf-8")
rt = template.render(calendar = rando_df, page=page)
ofh.write(rt)
ofh.close()

page="Correspondants"
template = env.get_template('./correspondants/correspondants.html.j2') #nomdutemplate
ofh = codecs.open("./correspondants/correspondants.html","w", encoding="utf-8")
rt = template.render(calendar = rando_df, page=page)
ofh.write(rt)
ofh.close()
