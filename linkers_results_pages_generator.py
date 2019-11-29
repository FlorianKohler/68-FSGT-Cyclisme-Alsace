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

def create_html_file(race):
    
    discipline=dict_discipline[race["Discipline"]]
    folder_path="./" + discipline

    

    redirect_address_result="./" + discipline + "/resultats/resultats_" + race["FileName"] + ".pdf"
    redirect_address_publi="./" + discipline + "/publications/publication_" + race["FileName"] + ".pdf"
    

    
    racename=race["FileName"]
    discipline_propre=race["Discipline"]
    nom_complet=race["Nom"]
    

    template = env.get_template('./redirect_page_template.html.j2') #nomdutemplate
    ofh = codecs.open(folder_path+"/fb/publication_" + racename + ".html","w", encoding="utf-8")
    rt = template.render(own_address="https://www.fsgt-cyclisme-alsace.fr/"+discipline+"/fb/publication_" + racename + ".html", address = redirect_address_publi, discipline=discipline, discipline_propre=discipline_propre, nom_complet=nom_complet, val="publi")
    ofh.write(rt)
    ofh.close()

    ofh = codecs.open(folder_path+"/fb/resultats_" + racename + ".html","w", encoding="utf-8")
    rt = template.render(own_address="https://www.fsgt-cyclisme-alsace.fr/"+discipline+"/fb/resultats_" + racename + ".html" , address = redirect_address_result, discipline=discipline, discipline_propre=discipline_propre, nom_complet=nom_complet, val="resul")
    ofh.write(rt)
    ofh.close()


dir_path=os.path.dirname(os.path.abspath(__file__))
#os.chdir(dname)

fsloader = jinja2.FileSystemLoader(dir_path) #dossier ou se trouve les template
env = jinja2.Environment(loader=fsloader)

df = pd.read_excel("Calendrier.xlsx")
df = df.replace(np.nan, "", regex=True)

dict_discipline = {'VTT': 'VTT', 'Route': 'route', 'Grimpée': 'grimpees', 'Randonnée': 'randonnees', 'Cyclo-cross' : "cyclo_cross"}

#df["lien_publi"] = "./" + df["Discipline"].map(dict_discipline) + "/publications/publication_" + df["FileName"] + ".pdf"
def j(a):
    return(a.startswith("http"))

df["lien_publi"] = np.where(df["FileName"].apply(j), df["FileName"],"./" + df["Discipline"].map(dict_discipline) + "/publications/publication_" + df["FileName"] + ".pdf")
df["lien_publi1"] = np.where(df["FileName"].apply(j), df["FileName"],"./" + df["Discipline"].map(dict_discipline) + "/publications/publication_" + df["FileName"] + "1.pdf")


# If it is a link : the link. Else : every thing else

df["lien_resul"] = np.where(df["FileName"].apply(j), df["FileName"], "./" + df["Discipline"].map(dict_discipline) + "/resultats/resultats_" + df["FileName"] + ".pdf")
df["lien_resul1"] = np.where(df["FileName"].apply(j), df["FileName"], "./" + df["Discipline"].map(dict_discipline) + "/resultats/resultats_" + df["FileName"] + "1.pdf")

#engagés ou horaires
df["lien_engages"] = "./" + df["Discipline"].map(dict_discipline) + "/publications/Liste_engages_" + df["FileName"] + ".pdf"
df["lien_horaires_depart"] = "./" + df["Discipline"].map(dict_discipline) + "/publications/Horaires_depart_" + df["FileName"] + ".pdf"

for index, race in df.iterrows():
    if j(race["FileName"])==False: # if the link is not already a link
        create_html_file(race)

        print(race['FileName'])







