from django.shortcuts import render
import xml.etree.ElementTree as ET
import requests

# Create your views here.
def home(request):
    response = requests.get('https://websvc.biocyc.org/apixml',
                            {'fn': 'genes-of-pathway', 'id':'ARA:PWY-82'})


    # response = requests.get('https://www.ebi.ac.uk/proteins/api/proteins',
    #                         {'taxid': '3702', 'id': 'ARA:AT5G52560'})
    root = ET.fromstring(response.content)
    # requestURL = "
    #
    # r = requests.get(requestURL, headers={"Accept": "application/xml"})
    for element in root.iter('Gene'):
        if 'ID' in element.attrib:
            print(element.attrib['frameid'])
    return render(request, "metabo/home.html", locals())
