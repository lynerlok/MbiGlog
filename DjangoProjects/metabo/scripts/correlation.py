import csv
import pandas as pd

def reader(data):
    txt = []
    with open(data, encoding="utf8", errors='ignore') as fichier:
        for line in fichier:
            txt.append(str(line).replace('\x00', ''))
    return txt


# Rentre les données en string dans un dictionnaire et le retourne
def strToFloat(data):
    dic = {}
    for line in data:
        res = line.split()
        if len(res) == 4:
            dic[str(res[0])] = [float(res[1]), float(res[2]), float(res[3])]
    return dic


# Effectue la correlation de Pearson sur la dataFrame
def corrPearson(data):
    correlation = pd.DataFrame(data)
    result_correlation = correlation.corr(method='pearson')
    return result_correlation


##Transforme la dataFrame en dictionnaire de dictionnaire qui peut etre facilement parcouru.
def translateMatrix(Pearsonmatrix):
    correlDict = Pearsonmatrix.to_dict()
    return correlDict


def meltDict(dict, seuil):
    output = []
    for geneA in dict.keys():
        for geneB, value in dict[geneA].items():
            if geneA != geneB and abs(value) >= seuil and (geneB, geneA, value) not in output:
                output.append([geneA, geneB, value, "correlation pair"])
    return output


def saveResult(output, path):
    fichier = open(path, "w")
    for i in output:
        for j in i:
            fichier.write(str(j) + '\t')
        fichier.write('\n')
    fichier.close()
