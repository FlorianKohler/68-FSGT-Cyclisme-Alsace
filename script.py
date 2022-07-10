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


def is_url(a):
    return(a.startswith("http"))

def is_dossardeur(a):
    return(a.startswith("Inscriptions via"))

df["publi_dossardeur"] = np.where(df["FileName"].apply(is_dossardeur), True, False)

df["lien_publi"] = np.where(df["FileName"].apply(is_url), df["FileName"],"./" + df["Discipline"].map(dict_discipline) + "/publications/publication_" + df["FileName"] + ".pdf")
df["lien_publi1"] = np.where(df["FileName"].apply(is_url), df["FileName"],"./" + df["Discipline"].map(dict_discipline) + "/publications/publication_" + df["FileName"] + "1.pdf")

# If it is a link : the link. Else : every thing else

df["lien_resul"] = np.where(df["FileNameResults"].apply(is_url), df["FileNameResults"], "./" + df["Discipline"].map(dict_discipline) + "/resultats/resultats_" + df["FileName"] + ".pdf")
df["lien_resul1"] = np.where(df["FileNameResults"].apply(is_url), df["FileNameResults"], "./" + df["Discipline"].map(dict_discipline) + "/resultats/resultats_" + df["FileName"] + "1.pdf")

#engagés ou horaires
df["lien_engages"] = "./" + df["Discipline"].map(dict_discipline) + "/publications/Liste_engages_" + df["FileName"] + ".pdf"
df["lien_horaires_depart"] = "./" + df["Discipline"].map(dict_discipline) + "/publications/Horaires_depart_" + df["FileName"] + ".pdf"

current_season_year = 2022

today = datetime.date.today()
if datetime.datetime.now().hour < 14:
    today = today - datetime.timedelta(1)

def file_exists(x):
    return os.path.isfile(x)

def get_file_time(x):
    if file_exists(x) == False:
        return 0
    return os.path.getmtime(x)

def get_date(date_string, current_season_year):

    '''Extracts  the date under datetime day format from the Date column of the xlsx file'''
    liste_mois={"janvier":1, "février":2, "mars":3, "avril":4, "mai":5, "juin":6, "juillet":7, "août":8, "septembre":9, "octobre":10, "novembre":11, "décembre":12}
    
    # examples : 23 et 24 janvier
    # examples : 12 janvier 2022
    # 23-24 janvier convient
    # 23,24 janvier ne convient pas

    day_found = False
    month_found = False
    date_string=str(date_string)
    date_string.replace("-", " ")
    date_string.replace(",", " ")
    date_string.replace("/", " ")
    year = current_season_year
    day = 100 # to make sure there's no error

    for elem in date_string.split():
        if elem.isdigit():
            if day_found==False and len(elem)<=2:
                day = int(elem)
                day_found = True
            elif len(elem)==4:
                year = int(elem)
        elif month_found==False and elem.lower() in liste_mois.keys():
            month = elem.lower()
            month_found = True


    if month_found == False or day_found == False or day>31:
        print(date_string)
        print("ATTENTION : Format de date incorrect")

    return datetime.date(year, liste_mois[month], day)


df["publi_dispo"] = False
df["publi1_dispo"] = False
df["resul_dispo"] = False
df["resul1_dispo"] = False
df["horaires_dispo"] = False
df["engages_dispo"] = False
df["date_obj"] = df["Date"].apply(get_date, current_season_year=current_season_year)

for i in range(len(df)):
    if is_url(df.iloc[i]['lien_publi']): #link
        df.iloc[i, df.columns.get_loc('publi_dispo')] = True
    if file_exists(df.iloc[i]['lien_publi']) == True:
        df.iloc[i, df.columns.get_loc('publi_dispo')] = (   datetime.datetime.strptime(time.ctime(get_file_time(df.iloc[i]['lien_publi'])), "%a %b %d %H:%M:%S %Y").year >= current_season_year   )
    if file_exists(df.iloc[i]['lien_publi1']) == True:
        df.iloc[i, df.columns.get_loc('publi1_dispo')] = (   datetime.datetime.strptime(time.ctime(get_file_time(df.iloc[i]['lien_publi1'])), "%a %b %d %H:%M:%S %Y").year >= current_season_year   )

    if is_url(df.iloc[i]['lien_resul']): #link
        df.iloc[i, df.columns.get_loc('resul_dispo')] = True
    if file_exists(df.iloc[i]['lien_resul']) == True:
        df.iloc[i, df.columns.get_loc('resul_dispo')] = (   datetime.datetime.strptime(time.ctime(get_file_time(df.iloc[i]['lien_resul'])), "%a %b %d %H:%M:%S %Y").year >= current_season_year  )
    if file_exists(df.iloc[i]['lien_resul1']) == True:
        df.iloc[i, df.columns.get_loc('resul1_dispo')] = (   datetime.datetime.strptime(time.ctime(get_file_time(df.iloc[i]['lien_resul1'])), "%a %b %d %H:%M:%S %Y").year >= current_season_year  )

    if file_exists(df.iloc[i]['lien_horaires_depart']) == True:
            #start list is displayed if : current_year is correct and race has not already taken place (date_race > today, with today starting at 2pm)
        df.iloc[i, df.columns.get_loc('horaires_dispo')] = (   datetime.datetime.strptime(time.ctime(get_file_time(df.iloc[i]['lien_horaires_depart'])), "%a %b %d %H:%M:%S %Y").year >= current_season_year and df.iloc[i]["date_obj"] > today)
    if file_exists(df.iloc[i]['lien_engages']) == True:
        #start list is displayed if : current_year is correct and race has not already taken place (date_race > today, with today starting at 2pm)
        df.iloc[i, df.columns.get_loc('engages_dispo')] = (   datetime.datetime.strptime(time.ctime(get_file_time(df.iloc[i]['lien_engages'])), "%a %b %d %H:%M:%S %Y").year >= current_season_year and df.iloc[i]["date_obj"] > today)

# For home page, find which the first course that has not happened (next one) 


##### bug when the year of the calendar is not the current year (ex : few first dates in January before the calendar is updated)
# today = datetime.date(2019, 12, 31) #Putting manually today to 31st December of previous year
##### Here an alternative which does not solve the problem

split = 0
# provisionary split is another one
split = len(df)-1 #really provisional with the championship cx coming
#if last race in calendar => nothing found

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

last_races_df = df[max(split-10,0): split] #taking 10 races to make sure we have still 4 after removing cancelled races

last_races_df = last_races_df[(~(last_races_df["Info"].str.contains('Annulé|Reporté', na=False)))] # if cancelled : no results so should not be displayed here.
last_races_df = last_races_df[last_races_df["Discipline"] != "Randonnée"] # if randonnée: no results so should not be displayed here.

last_races_df = last_races_df.tail(5) #taking the last five ones


next_races_df = df[split: min(len(df), split+4 )]
# maybe not here too. to be thought about.
# Start loop again on df


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
