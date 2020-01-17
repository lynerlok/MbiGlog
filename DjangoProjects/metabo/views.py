from django.shortcuts import render
import xml.etree.ElementTree as ET
import requests

# Create your views here.
def home(request):
    response = requests.get('https://www.ebi.ac.uk/proteins/api/proteins',
                             {'gene':'AT5G52560','organism': 'Arabidopsis thaliana','taxid': '3702'}, headers={"Accept": "application/xml"})
    root = ET.fromstring(response.text)
    content = response.content
    responseBody = response.text
    # balise = ['name','property']
    # for b in balise:
    for element in root:
        print(element)
        if len(element.attrib) == 0:
            print('okkk')
            print(element.text)
            # if 'entry name' in element.attrib['type']:
            #     print('ok')
    return render(request, "metabo/home.html", locals())
