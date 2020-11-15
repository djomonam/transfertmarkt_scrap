# -*- coding: utf-8 -*-
"""
Created on Sam Okt 14 17:45:12 2020

@author: Arnold Namegni
"""

import os
import csv
import requests
from bs4 import BeautifulSoup
import urllib
import json
import time

##Data Collection
class Ligue(object):	
	def __init__(self,uri,html):
		self.uri = uri
		self.html = html

class Club(object):
	def __init__(self,uri,html):
		self.uri = uri
		self.html = html
		
	def save(self):
		soup = BeautifulSoup(self.html,features='html.parser')
		titre = soup.find("title").text
		a = open("transfertmarkt_scraping/clubs/" + nettoyer(titre.split(' -')[0]) + ".html","wb")
		a.write(self.html)
		a.close()		

class Player(object):
	def __init__(self,uri,html):
		self.uri = uri
		self.html = html
		
	def save(self):
		soup = BeautifulSoup(self.html,features='html.parser')
		titre = soup.find("head").find("title")
		if titre is not None:
			a = open("transfertmarkt_scraping/players/" + nettoyer(titre.text.split(' -')[0]) + ".html","wb")
			a.write(self.html)
			a.close()
		
class Transfert(object):
	def __init__(self,uri_player,saison,uri_cluba,uri_clubb,montant):
		self.uri_player = uri_player
		self.saison = saison
		self.uri_clubsource = uri_cluba
		self.uri_clubdest = uri_clubb
		self.montant = montant
	
	def export_dict(self):
		dict = {
			"uri_player":self.uri_player,
			"saison":self.saison,
			"uri_clubsource":self.uri_clubsource,
			"uri_clubdest":self.uri_clubdest,
			"montant":self.montant
		}
		return dict

def getLigue(url):
	headers = {"User-Agent":"Mozilla/5.0"}
	requete = requests.get(url, headers=headers)
	page = requete.content
	return Ligue(url,page)
	
def getLigues():
	url= "https://www.transfermarkt.de/wettbewerbe/europa/"
	headers = {"User-Agent":"Mozilla/5.0"}
	requete = requests.get(url, headers=headers)
	page = requete.content
	soup = BeautifulSoup(page,features='html.parser')
	tableau = soup.find_all("tr",class_="odd") + soup.find_all("tr",class_="even")
	uris = []
	for t in tableau:
		uris.append("https://www.transfermarkt.de" + t.find_all("a")[1]["href"])
	return [getLigue(u) for u in uris]
	
def getClub(url):
	headers = {"User-Agent":"Mozilla/5.0"}
	requete = requests.get(url, headers=headers)
	page = requete.content
	return Club(url,page)

def getClubs(ligue):
	soup = BeautifulSoup(ligue.html,features='html.parser')
	temp = soup.find("div",attrs={"id":"yw1"})
	tableau = temp.find_all("tr",class_="odd") + temp.find_all("tr",class_="even")
	uris = []
	for t in tableau:
		uris.append("https://www.transfermarkt.de" + t.find_all("a")[1]["href"])
	return [getClub(u) for u in uris]
	
def getPlayer(url):
	headers = {"User-Agent":"Mozilla/5.0"}
	requete = requests.get(url, headers=headers)
	page = requete.content
	return Player(url,page)
	
def getPlayers(club):
	soup = BeautifulSoup(club.html, features='html.parser')
	tableau = soup.find_all("tr",class_="odd") + soup.find_all("tr",class_="even")
	uris = []
	for t in tableau:
		temp = t.find_all("a")
		if len(temp) > 3:
			if "*" not in temp[3].text:
				uris.append("https://www.transfermarkt.de" + temp[3]["href"])
		else:
			if "*" not in temp[1].text:
				uris.append("https://www.transfermarkt.de" + t.find_all("a")[1]["href"])
	return [getPlayer(u) for u in uris]
	
# ligues = getLigues()
# 
# print(" *** Recherche des clubs *** ")
# clubs = []
# A = 0
# for i in ligues:
# 	A+=1
# 	clubs = clubs + getClubs(i)
# 	print(str(A) + " / " + str(len(ligues)))
# 
# print(" *** Recherche des joueurs *** ")
# players = []
# A = 0	
# for i in clubs:
# 	A+= 1
# 	i.save()
# 	tmp = getPlayers(i)
# 	for j in tmp:
# 		players.append(j)
# 		j.save()
# 	print("État d'avancement : " + str(A) + " / " + str(len(clubs)))

##Traitement
def nettoyer(x):
	textToClean = x.replace("\n","").replace("\t","").replace("\r","").replace("\xa0","")
	textToClean = textToClean.translate(strring.makettrans("",""),string.ponctuation)
	return textToclean

def convert_prix(x):
	a = x.split(" mio")
	try:
		if len(a) > 1:
			b = a[0].split(",")
			return str(int(b[0]) * 1000000 + int(b[1]) * 10000)
		elif len(x.split(" K")) > 1:
			a = x.split(" K")
			return str(int(a[0]) * 1000)
		else:
			return str(x)		
	except ValueError:
		return str(x)

def convert_date(x):
	a = x.split("/")
	if len(a) == 1:
		return a[0]
	b = a[1]
	if len(b) > 2:
		return b
	else:
		if int(b) < 22 and len(a[0]) <= 2:
			return "20"+b
		else:
			return "19"+b

def extract_club_data(html):
	soup = BeautifulSoup(html)
	html_valeur = soup.find("div",class_="dataMarktwert").text
	valeur = convert_prix(html_valeur)	
	ligue = nettoyer(soup.find("span",class_="hauptpunkt").text).strip()
	pays = soup.find("div",class_="dataZusatzDaten").find("span",class_="mediumpunkt").find("img")["alt"]
	url = soup.find("meta",attrs={"property":"og:url"})["content"]
	uri_club = nettoyer(url.split("startseite/")[0])
	nom_club = nettoyer(soup.find("title").text.split(" -")[0])
	
	#Palmarès
	url_palmares = url.replace("startseite","erfolge")
	headers = {"User-Agent":"Mozilla/5.0"}
	requete = requests.get(url_palmares, headers=headers)
	html_palmares = requete.content
	soup = BeautifulSoup(html_palmares)
	palmares = soup.find_all("div",class_="erfolg_infotext_box")
	palmares_text = [nettoyer(p.text).split(",") for p in palmares]
	trophes = [0 for i in range(0,2020-1980)]
	for ligne in palmares_text:
		for saison in ligne:
			annee = int(convert_date(nettoyer(saison)))
			if annee >= 1980:
				trophes[annee-1980] += 1

	return [uri_club,nom_club,ligue,pays,valeur] + trophes
	
def extract_all_club_data():
	fichiers = os.listdir("clubs")
	B = len(fichiers)
	A = 0
	b = open("clubs.csv","a")
	for fichier_club in fichiers:
		A += 1
		a = open("clubs/" + fichier_club,"rb")
		data = extract_club_data(a.read())
		try:
			ligne = data[0]
			for i in range(1,len(data)):
				ligne += ";" + str(data[i])
			ligne += "\n"
			b.write(ligne)
		except UnicodeEncodeError:
			print("erreur d'encodage :: " + data[1])
		print("État d'avancement : " + str(A) + " / " + str(B))
	b.close()
	
def extract_player_data(html):
	soup = BeautifulSoup(html,'html.parser')
	url = soup.find("meta",attrs={"property":"og:url"})["content"]
	uri_player = url
	nom_joueur = soup.find("title").text.split(" -")[0]
	print(nom_joueur)
	html_valeur = soup.find("div",class_="dataMarktwert")
	if html_valeur is not None:
		html_valeur = html_valeur.text
		valeur = convert_prix(html_valeur)
	else:
		valeur = ""
	html_data = soup.find("table",class_="auflistung")
	tableau = html_data.find_all("tr")
	nom_origine_joueur = nom_joueur
	ligne1 = tableau[0].find("th").text
	geburtsdatum = ""
	position = ""
	if "name" in ligne1.lower():
		nom_origine_joueur = tableau[0].find("td").text
	for i in range(len(tableau)):
		key = nettoyer(tableau[i].find("th").text)
		if "geburtsdatum" in key.lower():
			geburtsdatum = tableau[i].find("td").find("a")["href"].split("/")[-1]
		elif "nationalit" in key.lower(): 
			nationalite = nettoyer(tableau[i].find("td").find("img")["alt"])
		elif "position" in key.lower() :
			position = nettoyer(tableau[i].find("td").text)
		elif "verein" in key.lower() :
			club_actuel = nettoyer(tableau[i].find("td").text)[1:-1]
			uri_club = "https://www.transfermarkt.de" + tableau[i].find("td").find("a")["href"].split("startseite/")[0]
			break
			
	#Palmarès
	url_palmares = url.replace("profil","erfolge")
	headers = {"User-Agent":"Mozilla/5.0"}
	requete = requests.get(url_palmares, headers=headers)
	html_palmares = requete.content
	soup = BeautifulSoup(html_palmares)
	palmares = soup.find_all("div",class_="erfolg_info_box")
	palmares_text = [nettoyer(p.find("td","erfolg_table_saison").text) for p in palmares]
	trophes = [0 for i in range(0,2020-1980)]
	for saison in palmares_text:
		annee = int(convert_date(saison))
		if annee >= 1980:
			trophes[annee-1980] += 1
	return [uri_player,nom_joueur,nom_origine_joueur,geburtsdatum,nationalite,position,club_actuel,uri_club,valeur] + trophes
	
def extract_all_player_data():
	fichiers = os.listdir("joueurs")      
	B = len(fichiers)
	A = 8252
	b = open("joueurs.csv","a")
	t1 = time.time()
	for i in range(A,B):
		fichier_joueur = fichiers[i]
		A += 1
		if A%100 == 0:
			t2 = time.time()
			print("Temps restant estimé : " + str((B - A) / 6000 * (t2 - t1)))
			t1 = t2
		a = open("transfertmarkt_scraping/players/" + fichier_joueur,"rb")
		data = extract_player_data(a.read())
		try:
			ligne = data[0]
			for i in range(1,len(data)):
				ligne += ";" + str(data[i])
			ligne += "\n"
			b.write(ligne)
		except:
			print("joueur pourri")
		print("État d'avancement : " + str(A) + " / " + str(B))
	b.close()

def all_transferts():
	fichiers = os.listdir("clubs")
	B = len(fichiers)
	A = 0
	for fichier_club in fichiers:
		A += 1
		a = open("clubs/" + fichier_club,"rb")
		soup = BeautifulSoup(a.read())
		url = soup.find("meta",attrs={"property":"og:url"})["content"]
		gauche = url.split("/startseite/")[0]
		identifiant = url.split("startseite")[1].split("/")[2]
		url_transferts = gauche + "/alletransfers/verein/"+identifiant
		headers = {"User-Agent":"Mozilla/5.0"}
		titre = soup.find("title").text
		requete = requests.get(url_transferts, headers=headers)
		page = requete.content
		b = open("transferts/"+titre.split('|')[0].split("/")[0]+".html","wb")
		b.write(page)
		b.close()
		a.close()
		print("État d'avancement : " + str(A) + " / " + str(B))

def extract_data_transferts(html):
	soup = BeautifulSoup(html)
	tableaux = soup.find_all("div",class_="large-6 columns")
	url = soup.find("meta",attrs={"property":"og:url"})["content"]
	uri_base = url.split("alletransfers/")[0]
	nom_base = soup.find("title").text.split(" -")[0]
	entrees = []
	for i in range(len(tableaux)):
		t = tableaux[i]
		if i%2 == 0:
			saison = t.find("div",class_="table-header").text.split("Arrivées ")[1].split("\t")[0]
			body = t.find_all("tbody")
			if len(body) > 0:
				body = body[0]
				lignes = body.find_all("tr")
				for l in lignes:
					html_joueur = l.find("td",class_="hauptlink").find("a")
					html_club = l.find("td",class_="no-border-links").find("a")
					html_prix = l.find("td",class_="rechts")
					
					uri_joueur = "http://www.transfermarkt.de" + html_joueur["href"]
					nom_joueur = html_joueur.text
					prix = html_prix.text
					target = uri_base
					source = "http://www.transfermarkt.de" + html_club["href"].split("transfers")[0]
					nom_dest = nom_base
					nom_source = html_club.text
					entrees.append([source,target,convert_date(saison),uri_joueur,nom_joueur,nom_source,nom_dest,convert_prix(prix)])
				
			
		else:
			saison = t.find("div",class_="table-header").text.split("Départs ")[1].split("\t")[0]
			body = t.find_all("tbody")
			if len(body) > 0:
				body = body[0]
				lignes = body.find_all("tr")
				for l in lignes:
					html_joueur = l.find("td",class_="hauptlink").find("a")
					html_club = l.find("td",class_="no-border-links").find("a")
					html_prix = l.find("td",class_="rechts")
					
					uri_joueur = "http://www.transfermarkt.de" + html_joueur["href"]
					nom_joueur = html_joueur.text
					prix = html_prix.text
					source = uri_base
					target = "http://www.transfermarkt.de" + html_club["href"].split("transfers")[0]
					nom_source = nom_base
					nom_dest = html_club.text
					entrees.append([source,target,convert_date(saison),uri_joueur,nom_joueur,nom_source,nom_dest,convert_prix(prix)])
	
	return entrees

def extract_all_transfert_data():
	fichiers = os.listdir("transferts")
	B = len(fichiers)
	A = 0
	C = 0
	D = 0
	for fichier_club in fichiers:
		A += 1
		a = open("transferts/" + fichier_club,"rb")
		data = extract_data_transferts(a.read())
		b = open("transferts.csv","a")
		for i in data:
			st = ""
			for k in i:
				st += k + ";"
			st += "\n"
			try: 
				b.write(st)
				D += 1
			except UnicodeEncodeError:
				C += 1
		b.close()
		print("État d'avancement : " + str(A) + " / " + str(B))
	print("En tout, "+ str(D) + " transferts ont été analysés")
	print("Mais " + str(C) + " n'ont pas été analysés à cause de noms pourris")


def extract_all_leagues_ranking():
	ligues = getLigues()
	B = len(ligues) * 27
	A = 0
	a = open("classements_saison_clubs_ligues.csv","a")
	for l in ligues:
		uri = l.uri
		for i in range(1980,2017):
			url_classement = uri.replace("startseite","tabelle") + "/saison_id/" + str(i)
			headers = {"User-Agent":"Mozilla/5.0"}
			requete = requests.get(url_classement, headers=headers)
			page = requete.content
			soup = BeautifulSoup(page)
			try:
				tableau = soup.find("div",class_="responsive-table").find("table").find("tbody")
			except AttributeError:
				print("Oh, voilà une année ou la ligue que je suis en train de chercher n'existait pas !")
			entrees = tableau.find_all("tr")
			for k in range(len(entrees)):
				annee = str(i+1)
				rang = str(k+1)
				a_club = entrees[k].find("a")
				nom_club = a_club.text
				uri_club = "http://www.transfermarkt.de" + a_club["href"].split("spielplan/")[0]
				a.write("\n" + uri_club + ";" + nom_club + ";" + annee + ";" + rang + ";" + uri)


			A += 1
			print("État d'avancement : " + str(A) + " / " + str(B))
	print("Enfin terminé !")
	a.close()