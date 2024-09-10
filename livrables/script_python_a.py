import time
import glob
import csv
import os
import json
import xml.etree.ElementTree as ET
# https://fr.wikipedia.org/wiki/Liste_des_codes_ISO_639-2
# https://gist.github.com/carlopires/1262033/c52ef0f7ce4f58108619508308372edd8d0bd518
# https://www.loc.gov/standards/iso639-2/php/code_list.php


debut = time.time()

def obtenir_identifiant_ark(identifier):
    return identifier.split("/12148/")[1]

# scriptPath = os.path.realpath(__file__)
# rootPath = os.path.dirname(scriptPath)

repo_mss = "/Users/mpappia/Desktop/parse/oai_mss"
output_folder = "/Users/mpappia/Desktop/parse/langues_data"
output_json = "/Users/mpappia/Desktop/parse/results.json"

data_all = {}

for filepath in glob.glob(f'{repo_mss}/*.xml'):
    try:
        tree = ET.parse(filepath)
        root = tree.getroot()

        xpath_lang = ".//{http://purl.org/dc/elements/1.1/}language"

        xpath_desc = ".//{http://purl.org/dc/elements/1.1/}description"

        xpath_source_dc = ".//{http://purl.org/dc/elements/1.1/}source"
        xpath_source = ".//source" # 2 chemins
        xpath_date_dc = ".//{http://purl.org/dc/elements/1.1/}date"
        xpath_date = ".//date" # 2 chemins
        
        xpath_identifier = ".//header/identifier"

        # Etablissement de la liste des codes langues, et analyse de la longueur de la liste
        langList = [element.text.lower() for element in root.findall(xpath_lang) if element.text is not None]

        if len(langList) == 0:
            lang = "non spécifiée"
        elif len(langList) > 1:
            lang = "multi-langues"
        else:
            lang = langList[0]

        if lang not in data_all:
            data_all[lang] = {"Nombre_documents": 0, "Documents": {}}

        document_data = {}

        identifier_element = root.find(xpath_identifier)
        if identifier_element is not None:
            identifier_ark = obtenir_identifiant_ark(identifier_element.text)
        else:
            identifier_ark = "Ark non identifié"

        document_data["ID"] = identifier_element.text if identifier_element is not None else "ID non trouvée"

        source_element = root.find(xpath_source)
        document_data["Source"] = source_element.text if source_element is not None else "Source non trouvée"

        date_element = root.find(xpath_date)
        document_data["Date"] = date_element.text if date_element is not None else "Date non trouvée"

        lang_texts = [element.text for element in root.findall(xpath_lang) if element.text]
        document_data["Langue"] = ", ".join(lang_texts) if lang_texts else "Non Spécifiée"

        desc_texts = [element.text or "" for element in root.findall(xpath_desc)]
        document_data["Description"] = "; ".join(desc_texts) if desc_texts else "Description non trouvée"

        data_all[lang]["Documents"][identifier_ark] = document_data
        data_all[lang]["Nombre_documents"] += 1

    except Exception as e:
        print(f"Erreur sur le fichier {filepath}: {e}")

fin = time.time()
temps = fin - debut
print(f"Temps d'exécution : {temps} secondes")

with open(output_json, 'w') as json_file:
    json.dump({
        lang: {
            "Nombre_documents": data["Nombre_documents"],
            "Documents": {ark: {key: value for key, value in doc.items() if key != "ID"} for ark, doc in data["Documents"].items()}
        }
        for lang, data in data_all.items()
    }, json_file, indent=4)

os.makedirs(output_folder, exist_ok=True)

for lang, lang_data in data_all.items():
    lang_csv_file = os.path.join(output_folder, f"{lang}.csv")
    with open(lang_csv_file, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["ID", "Source", "Date", "Langue", "Description"])
        writer.writerows([doc.values() for doc in lang_data["Documents"].values()])

print("Done")