import time
import glob
import os
import xml.etree.ElementTree as ET
import re
import json

# Timer
debut = time.time()

# Chemins
scriptPath = os.path.realpath(__file__)  # Chemin du présent script
rootPath = os.path.dirname(scriptPath)  # Chemin du dossier le contenant

repo_mss = f"{rootPath}/oai_mss"
output_folder = f"{rootPath}/temp"
output_json = f"{output_folder}/dates.json"

datesDict={}

for filepath in glob.glob(f'{repo_mss}/*.xml'):
    tree = ET.parse(filepath)
    root = tree.getroot()
    xpath_date = ".//{*}date"  # xpath. Attention pas de wildcard supportée en Python < 3.8
    identifier = ".//{*}identifier"

    datesList =[]

    for element in root.findall(xpath_date):
        if element.text and element.text not in datesList:
            datesList.append(element.text)

    if len(datesList)==1:        
        for i in datesList:
            if re.fullmatch(r"\d{4}", i):
                identifier_element = root.find(identifier)
                if identifier_element is not None:
                    identifier_element = identifier_element.text.split("/12148/")[1]
                    r = re.search(r"\d{4}", i)
                    if r is not None:
                        datesDict[identifier_element] = r.group(0)
            else:
                r = re.search(r"(1\d{3}|1\d[\d\.]\.)", i)
                if r != None:
                    identifier_element = root.find(identifier)
                    identifier_element = identifier_element.text.split("/12148/")[1]
                    datesDict[identifier_element] = r.group(0)
                    

with open(output_json, 'w') as json_file:
    json.dump(datesDict, json_file, indent=4)


# Suivi console
fin = time.time()
temps = fin - debut
print(f"Temps d'exécution : {temps} secondes")
