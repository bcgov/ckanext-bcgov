# output ckan contents that are datasets
import csv
import re
import StringIO
import requests
# import ckanapi_exporter.exporter as exporter

def parseString(input,i):
    for x in csv.reader(StringIO.StringIO(input), delimiter=','):
        return x[i]

def export_type(env):
    data_type = ['Geographic', 'Dataset', 'Application', 'WebService']


    groups = {}

    for d in data_type:
        print(d)

        with open(env+'.csv','rb') as w:
            reader = csv.reader(w)
            with open(d + '.csv', 'wb') as f:
                writer = csv.writer(f)
                firstline = True
              
                for row in reader:
                    if firstline:
                        if d == "Application" or d == 'WebService':
                            writer.writerow(row[:-2])
                        elif d == "Dataset":
                            writer.writerow(row[:-1])
                        else:
                            writer.writerow(row)
                        firstline = False
                        continue

                    # Select resource type to output
                    if row[2] == d:  
                        recs = row[15] # get urls
                        # get urls as list
                        # print 'REC: ', recs

                        # print recs
                        urls=re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),#]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', recs)

                        # print ' '
                        sub_org = row[5]

                        #build full organization dict
                        if sub_org in groups:
                            org = groups[sub_org].replace("-"," ").title() + ", "+sub_org
                        else:
                            org_url = 'https://'+env+'.data.gov.bc.ca/api/3/action/organization_show?id='+row[4].lower().replace(" ","-").replace(",","").replace("---","-").replace("'","-")
                            request = requests.get(org_url).json()["result"]["groups"][0]["name"]
                            groups[sub_org] = request
                            org = groups[sub_org].replace("-"," ").title() + ", "+sub_org

                        # cycle through each url and collect each corresponding entry in other columns
                        for i, url in enumerate(urls):
                            format = parseString(row[-5],i)
                            res_name = parseString(row[-4],i)
                            res_id = parseString(row[-3],i)
                            res_ty = parseString(row[-2],i)
                            
                            if d != "Geographic": 
                                # rows hardcoded. Not ideal...   
                                writer.writerow([row[0],row[1],row[2],row[3],row[4],org,row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]+'...',row[14],url,format,res_name,res_id,res_ty])
                            else:
                                writer.writerow([row[0],row[1],row[2],row[3],row[4],org,row[6],row[7],row[8],row[9],row[10],row[11],row[12],row[13]+'...',row[14],url,format,res_name,res_id,res_ty,row[-1]])

if __name__ == "__main__":
    export_type(env)
