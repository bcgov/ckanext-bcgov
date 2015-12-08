# output ckan contents that are datasets
import csv
import re
import StringIO
import requests
# import ckanapi_exporter.exporter as exporter

def parseString(input):
    for x in csv.reader(StringIO.StringIO(input), delimiter=','):
        return x[i]

data_type = ['geographic', 'dataset', 'application', 'webservice']

groups = {}

for d in data_type:
    print(d)

    with open('catalogue.csv','rb') as w:
        reader = csv.reader(w)
        with open(d + '.csv', 'wb') as f:
            writer = csv.writer(f)
            firstline = True
          
            for row in reader:
                if firstline:
                    if d == "Application" or d == 'WebService':
                        writer.writerow(row[:-1])
                    else:
                        writer.writerow(row)
                    firstline = False
                    continue

                # Select resource type to output
                if row[2] == d:  
                    recs = row[15] # get urls
                    # get urls as list
                    urls=re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', recs)
                    sub_org = row[5]

                    #build full organization dict
                    if sub_org in groups:
                        org = groups[sub_org].replace("-"," ").title() + ", "+sub_org
                    else:
                        org_url = 'http://catalogue.data.gov.bc.ca/api/3/action/organization_show?id='+row[4].lower().replace(" ","-").replace(",","").replace("---","-").replace("'","-")
                        request = requests.get(org_url).json()["result"]["groups"][0]["name"]
                        groups[sub_org] = request
                        org = groups[sub_org].replace("-"," ").title() + ", "+sub_org

                    # cycle through each url and collect each corresponding entry in other columns
                    for i, url in enumerate(urls):
                        format = parseString(row[-4])
                        res_name = parseString(row[-3])
                        res_id = parseString(row[-2])
                        res_ty = parseString(row[-1])
                        
                        # rows hardcoded. Not ideal...   
                        writer.writerow([row[0],row[1],row[2],row[3],row[4],org,row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]+'...',row[14],url,format,res_name,res_id,res_ty])


