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

today = datetime.date.today()
if datetime.datetime.now().hour < 14:
    today = today - datetime.timedelta(1)

current_year = today.year
current_month = today.month

def f(x):
    return os.path.isfile(x)
def g(x):
    if f(x) == False:
        return 0
    return os.path.getmtime(x)

def get_date(date_string):
    '''Extracts  the date under datetime day format from the Date column of the xlsx file'''
    liste_mois={"janvier":1, "février":2, "mars":3, "avril":4, "mai":5, "juin":6, "juillet":7, "août":8, "septembre":9, "octobre":10, "novembre":11, "décembre":12}
    day_found = False
    month_found = False
    date_string=str(date_string)

    for elem in date_string.split():
        if day_found==False and elem.isdigit():
            day = int(elem)
            day_found = True
        elif month_found==False and elem.lower() in liste_mois.keys():
            month = elem.lower()
            month_found = True

    if month_found == False or day_found == False or day>31:
        print("ATTENTION : Format de date incorrect")

    return datetime.date(2019, liste_mois[month], day)

df["publi_dispo"] = False
df["publi1_dispo"] = False
df["resul_dispo"] = False
df["resul1_dispo"] = False
df["horaires_dispo"] = False
df["engages_dispo"] = False
df["date_obj"] = df["Date"].apply(get_date)

for i in range(len(df)):
    if j(df.iloc[i]['lien_publi']): #link
        df.iloc[i, df.columns.get_loc('publi_dispo')] = True
    if f(df.iloc[i]['lien_publi']) == True:
        df.iloc[i, df.columns.get_loc('publi_dispo')] = (   datetime.datetime.strptime(time.ctime(g(df.iloc[i]['lien_publi'])), "%a %b %d %H:%M:%S %Y").year == 2019   )
    if f(df.iloc[i]['lien_publi1']) == True:
        df.iloc[i, df.columns.get_loc('publi1_dispo')] = (   datetime.datetime.strptime(time.ctime(g(df.iloc[i]['lien_publi1'])), "%a %b %d %H:%M:%S %Y").year == 2019   )

    if f(df.iloc[i]['lien_resul']) == True:
        df.iloc[i, df.columns.get_loc('resul_dispo')] = (   datetime.datetime.strptime(time.ctime(g(df.iloc[i]['lien_resul'])), "%a %b %d %H:%M:%S %Y").year == 2019    )
    if f(df.iloc[i]['lien_resul1']) == True:
        df.iloc[i, df.columns.get_loc('resul1_dispo')] = (   datetime.datetime.strptime(time.ctime(g(df.iloc[i]['lien_resul1'])), "%a %b %d %H:%M:%S %Y").year == 2019   )

    if f(df.iloc[i]['lien_horaires_depart']) == True:
            #start list is displayed if : current_year is correct and race has not already taken place (date_race > today, with today starting at 2pm)
        df.iloc[i, df.columns.get_loc('horaires_dispo')] = (   datetime.datetime.strptime(time.ctime(g(df.iloc[i]['lien_horaires_depart'])), "%a %b %d %H:%M:%S %Y").year == 2019 and df.iloc[i]["date_obj"] > today)
    if f(df.iloc[i]['lien_engages']) == True:
        #start list is displayed if : current_year is correct and race has not already taken place (date_race > today, with today starting at 2pm)
        df.iloc[i, df.columns.get_loc('engages_dispo')] = (   datetime.datetime.strptime(time.ctime(g(df.iloc[i]['lien_engages'])), "%a %b %d %H:%M:%S %Y").year == 2019 and df.iloc[i]["date_obj"] > today)

# For home page, find which the first course that has not happened (next one)
split = 0
for i in range(len(df)):
    if df.iloc[i]["date_obj"] >= today: #link
        if df.iloc[i]["date_obj"] == today:
            # Une course aujourd'hui est consideree comme une course passee
            j=i+1
            while df.iloc[j]["date_obj"] == today:
                j+=1
            split = j
        else:
            split = i
        break

last_races_df = df[max(split-5,0): split]
last_races_df = last_races_df[last_races_df["Info"] != "Annulé"] # if cancelled : no results so should not be displayed here.
last_races_df = last_races_df[last_races_df["Discipline"] != "Randonnée"] # if randonnée: no results so should not be displayed here.
#Careful : might lead to super small last_races_df !


next_races_df = df[split: min(len(df), split+4 )]
# maybe not here too. to be thought about.

route_df = df[df["Discipline"] == "Route"]
vtt_df = df[df["Discipline"] == "VTT"]
cyclocross_df = df[df["Discipline"] == "Cyclo-cross"]
grimpees_df = df[df["Discipline"] == "Grimpée"]
rando_df = df[df["Discipline"] == "Randonnée"]

page="Accueil"
template = env.get_template('index.html.j2') #nomdutemplate
ofh = codecs.open("index.html","w", encoding="utf-8")
rt = template.render(page=page, last_calendar = last_races_df, next_calendar = next_races_df)
ofh.write(rt)
ofh.close()

page="Archives"
template = env.get_template('archives.html.j2') #nomdutemplate
ofh = codecs.open("archives.html","w", encoding="utf-8")
rt = template.render(page=page, last_calendar = last_races_df, next_calendar = next_races_df)
ofh.write(rt)
ofh.close()


page="Route"
template = env.get_template('route.html.j2') #nomdutemplate
ofh = codecs.open("route.html","w", encoding="utf-8")
rt = template.render(calendar = route_df, page=page, last_calendar = last_races_df, next_calendar = next_races_df)
ofh.write(rt)
ofh.close()

page="VTT"
template = env.get_template('vtt.html.j2') #nomdutemplate
ofh = codecs.open("vtt.html","w", encoding="utf-8")
rt = template.render(calendar = vtt_df, page=page, last_calendar = last_races_df, next_calendar = next_races_df)
ofh.write(rt)
ofh.close()

page="Cyclocross"
template = env.get_template('cyclocross.html.j2') #nomdutemplate
ofh = codecs.open("cyclocross.html","w", encoding="utf-8")
rt = template.render(calendar = cyclocross_df, page=page, last_calendar = last_races_df, next_calendar = next_races_df)
ofh.write(rt)
ofh.close()

page="Grimpees"
template = env.get_template('grimpees.html.j2') #nomdutemplate
ofh = codecs.open("grimpees.html","w", encoding="utf-8")
rt = template.render(calendar = grimpees_df, page=page, last_calendar = last_races_df, next_calendar = next_races_df)
ofh.write(rt)
ofh.close()

page="Randonnees"
template = env.get_template('randonnees.html.j2') #nomdutemplate
ofh = codecs.open("randonnees.html","w", encoding="utf-8")
rt = template.render(calendar = rando_df, page=page, last_calendar = last_races_df, next_calendar = next_races_df)
ofh.write(rt)
ofh.close()

page="Liens"
template = env.get_template('./liens/liens.html.j2') #nomdutemplate
ofh = codecs.open("./liens/liens.html","w", encoding="utf-8")
rt = template.render(calendar = rando_df, page=page, last_calendar = last_races_df, next_calendar = next_races_df)
ofh.write(rt)
ofh.close()

page="Documents"
template = env.get_template('./documents/documents.html.j2') #nomdutemplate
ofh = codecs.open("./documents/documents.html","w", encoding="utf-8")
rt = template.render(calendar = rando_df, page=page, last_calendar = last_races_df, next_calendar = next_races_df)
ofh.write(rt)
ofh.close()

page="CommissionAlsace"
template = env.get_template('./commission_alsace/commission_alsace.html.j2') #nomdutemplate
ofh = codecs.open("./commission_alsace/commission_alsace.html","w", encoding="utf-8")
rt = template.render(calendar = rando_df, page=page, last_calendar = last_races_df, next_calendar = next_races_df)
ofh.write(rt)
ofh.close()

page="Commissaires"
template = env.get_template('./commissaires/commissaires.html.j2') #nomdutemplate
ofh = codecs.open("./commissaires/commissaires.html","w", encoding="utf-8")
rt = template.render(calendar = rando_df, page=page, last_calendar = last_races_df, next_calendar = next_races_df)
ofh.write(rt)
ofh.close()

page="Correspondants"
template = env.get_template('./correspondants/correspondants.html.j2') #nomdutemplate
ofh = codecs.open("./correspondants/correspondants.html","w", encoding="utf-8")
rt = template.render(calendar = rando_df, page=page, last_calendar = last_races_df, next_calendar = next_races_df)
ofh.write(rt)
ofh.close()
