import pandas as pd
import requests
from bs4 import BeautifulSoup
import geopandas as gpd
import os
API_KEY = "AIzaSyAEteJ0L565ARbnZcBaOtsy11ECE_lZZsU"
df = pd.read_csv(r'C:\Users\Razvan baban\Desktop\Licenta\baza-de-date-localitati-romania-master\date\Coordonate_localitati.csv')
dataframe_judete_abrevieri_judete = pd.DataFrame(df, columns=['judet', 'abreviere'])
caractere_de_inlocuit={'ă':'a', 'î':'i', 'â':'a', 'ș':'s', 'ț':'t'}
Lista_oferte = []
Lista_detalii = []
Lista_pret = []
Lista_localitate = []
Lista_judet = []
Lista_zona = []
Lista_link = []
Lista_latitudine_oras = []
Lista_longitudine_oras = []
url_base = "https://homezz.ro/anunturi_"
url_vanzare_inchiriere = input("Doresti sa cauti anunturi de vanzare sau de inchiriere?")
if url_vanzare_inchiriere == "inchiriere":
    url_anunt = input("Ce tipuri de anunțuri doresti sa cauti?\n"
                      "Toate din inchirieri\n"
                      "Apartamente\n"
                      "Garsoniere\n"
                      "Case-Vile\n"
                      "Terenuri\n"
                      "Birouri-Spații comerciale\n"
                      ":").lower()+"_de-inchiriat"
    if url_anunt == "toate din inchirieri":
        url_anunt = "de-inchiriat"
else:
    url_anunt = input("Ce tipuri de anunțuri doresti sa cauti?\n"
                      "Toate din vanzari\n"
                      "Apartamente\n"
                      "Garsoniere\n"
                      "Case-Vile\n"
                      "Terenuri\n"
                      "Birouri-Spații comerciale\n"
                      ":").lower()
    if url_anunt == "toate din vanzari":
        url_anunt = "de-vanzare"
url_locatie = input("Doresti sa cauti oferte in toata tara sau intr-un judet?").lower()
if url_locatie == "toata tara":
    url = url_base + url_anunt + ".html"
else:
    judet = input("În ce județ dorești să cauți anunțuri?").lower()
    url_judet_sau_localitate = input("Doresti sa cauti in tot judetul sau intr-o localitate specifica?").lower()

    if url_judet_sau_localitate == "tot judetul":
        if judet == "ilfov":
            url= url_base + url_anunt + "_in-" + "bucuresti-ilfov" + ".html"
        else:
            url = url_base + url_anunt + "_in-" + judet + ".html"
    else:
        url_judet = dataframe_judete_abrevieri_judete.loc[dataframe_judete_abrevieri_judete["judet"] == judet.capitalize()]
        url_judet_abreviere = str(url_judet['abreviere'].values[0]).lower()

        url_localitate = (input("În ce localitate dorești să cauți anunțuri?").lower()).replace(" ", "-")
        url = url_base + url_anunt + "_in-" + url_localitate + "-" + url_judet_abreviere + ".html"
print(url)
def extragere_date(url):
    response = requests.get(url)
    print(response)
    soup = BeautifulSoup(response.content, "html.parser")
    if soup.find(class_="last_page"):
        pagini = int(soup.find(class_="last_page").get_text())
    else:
        pagini=2
    print(pagini)
    Lista_pagini = list(range(1, pagini + 1))
    for numar_pagina_web in Lista_pagini:
        url_1 = url.replace(f".html", f"_{numar_pagina_web}.html")
        print(f"scraping:{url_1}")
        response_2 = requests.get(url_1)
        print(response_2)
        soup = BeautifulSoup(response_2.content, "html.parser")
        for reclame in soup.find_all(class_="residence_top_list main_items item_cart"):
            print(reclame)
            reclame.decompose()
            print(reclame)
        Oferte = soup.find(class_="list_grid")
        Nume_oferta = Oferte.find_all(class_="title")
        for nume in Nume_oferta:
            nume_text = nume.get_text()
            for key,value in caractere_de_inlocuit.items():
                nume_text=nume_text.replace(key,value)
            Lista_oferte.append(nume_text)
        Detalii_tehnice = Oferte.find_all(class_="info_details")
        for detalii in Detalii_tehnice:
            detalii_text = detalii.get_text().replace("  •  ","-")
            for key,value in caractere_de_inlocuit.items():
                detalii_text=detalii_text.replace(key,value)
            Lista_detalii.append(detalii_text)
        Pret = Oferte.find_all(class_="price")
        for pret in Pret:
            pret_text = pret.get_text().replace(".", "").replace(" eur", "")
            Lista_pret.append(pret_text)
        Locatie = Oferte.find_all(class_="location grid_location")
        for locatie in Locatie:
            locatie_text = locatie.get_text()
            Localitate_si_judet = locatie_text.split(", ")
            localitate = ((Localitate_si_judet[0].replace(" ", "")).replace("-", "")).capitalize()
            Lista_localitate.append(localitate)
            judet = Localitate_si_judet[1]
            Lista_judet.append(judet)
            zona = Localitate_si_judet[2]
            Lista_zona.append(zona)
            adresa = f"Romania+{judet}+{localitate}+{zona}"
            parametrii_google_api = { 'key': API_KEY,'address': adresa.replace(' ', '+')  }
            url_google_api = 'https://maps.googleapis.com/maps/api/geocode/json?'
            if numar_pagina_web == 300:
                response = requests.get(url_google_api, params=parametrii_google_api)
                data = response.json()
            else:
                response = requests.get(url_google_api, params=parametrii_google_api)
                data = response.json()
            if data['status'] == 'OK':
                result = data['results'][0]
                location = result['geometry']['location']
                latitudine_oras = location['lat']
                longitudine_oras = location['lng']
                Lista_latitudine_oras.append(latitudine_oras)
                Lista_longitudine_oras.append(longitudine_oras)
            else:
                print("eroare")
        Link = Oferte.find_all("a", href=True)
        for link in Link:
            if "residence_top_list main_items item_cart" in link:
                continue# Omitem anunțurile promovate
            else:
                start = ' href="'
                end = '"'
                link = str(link)
                link_text = ((link.split(start))[1].split(end)[0])
                if "https://homezz.ro/" not in link_text or "panorama-city" in link_text or "subcetate" in link_text:
                    continue
                else:
                    print(link_text)
                    Lista_link.append(link_text)
        if len(Lista_oferte)<len(Lista_link):
            del Lista_link[-1]
        print(len(Lista_link))
        print(len(Lista_oferte))
        print(len(Lista_pret))
    Dictionar_oferte = {"Oferta": Lista_oferte, "Oras": Lista_localitate, "Judet": Lista_judet, "Pret": Lista_pret,
                        "Detalii": Lista_detalii, "Link": Lista_link, "Zona": Lista_zona,
                        "Lat": Lista_latitudine_oras, "Long": Lista_longitudine_oras}
    df_oferte = pd.DataFrame(Dictionar_oferte, columns=["Oferta", "Oras", "Judet", "Pret",
                                                        "Detalii", "Link", "Zona", "Lat", "Long"])
    nume_csv = input("cum doresti sa se numeasca CSV-ul? :")
    df_oferte.to_csv(fr'C:\Users\Razvan baban\Desktop\Licenta\Program final python licenta\{nume_csv}.csv', index=False,
                     header=True)
    xy_table = pd.read_csv(fr'C:\Users\Razvan baban\Desktop\Licenta\Program final python licenta\{nume_csv}.csv')
    xy_gdf = gpd.GeoDataFrame(xy_table, geometry=gpd.points_from_xy(xy_table['Long'], xy_table['Lat']))
    print(xy_gdf)
    xy_gdf.plot(markersize=1.5, figsize=(10, 10))
    print(xy_gdf)
    xy_gdf = xy_gdf.set_crs("EPSG:4326")
    print(xy_gdf)
    nume_sph = input("cum doresti sa se numeasca fisierul shp?: ")
    xy_gdf.to_file(filename=f"{nume_sph}.shp", driver='ESRI Shapefile')
    os.startfile(fr"C:\Users\Razvan baban\Desktop\Licenta\Program final python licenta\Python proiect final\final\{nume_sph}.shp")


extragere_date(url)
