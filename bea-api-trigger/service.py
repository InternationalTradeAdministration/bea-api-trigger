import requests as r
import csv
import tempfile
from azure.storage.blob.blockblobservice import BlockBlobService as bbs
import os, re

conn_str = os.environ["AzureWebJobsStorage"]
acct_name = re.search('AccountName=(.+?);', conn_str).group(1)
acct_key = re.search('AccountKey=(.+?);', conn_str).group(1)
user_id = os.environ["user_id"]

def handler():
    base_api_url = 'https://apps.bea.gov/api/data?userID='+user_id+'&'

    ita = 'datasetname=ita&'

    ita_indicators = 'indicator=expgdsserv&indicator=expgds&indicator=expserv'

    intlservtrade = 'datasetname=intlservtrade&'

    ist_services = "TypesOfService=alltypesofservice,transportairpass,travel,travelbusiness,travelbusinessoth,traveleducation,travelhealth,travelpersonal,travelpersonaloth,travelshorttermwork"

    getCountries = base_api_url+'&method=getParameterValues&'+ita + "&parametername=areaorcountry"

    results_countries = r.get(getCountries)

    ita_countries = []
    for country in results_countries.json()['BEAAPI']['Results']['ParamValue']:
        ita_countries.append(country['Key'])

    ita_data = []
    ita_countries.remove('AllCountries')
    country = 'Africa'
    query = base_api_url+'method=getData&'+ita+ita_indicators+'&areaorcountry='+country
    write_row = []

    temp_ita_file = tempfile.NamedTemporaryFile(mode="r+", delete=False)

    block_blob_service = bbs(account_name = acct_name, account_key = acct_key)
    print(conn_str)
    with open(temp_ita_file.name, 'w+') as itacsvfile:
        ita_headers = r.get(query).json()['BEAAPI']['Results']['Dimensions']
        for header in ita_headers:
            write_row.append(header['Name'])
        ita_writer = csv.writer(itacsvfile, delimiter=',', quotechar='"', quoting = csv.QUOTE_MINIMAL)
        write_row.append('Notes')
        ita_writer.writerow(write_row)
        for country in ita_countries:
            write_row = []
            query = base_api_url+'method=getData&'+ita+ita_indicators+'&areaorcountry='+country 
            temp_store = r.get(query).json()
            print(query)
            if 'Data' in temp_store['BEAAPI']['Results'].keys():
                ita_results = temp_store['BEAAPI']['Results']['Data']
                for record in ita_results:
                    write_row=[]
                    for key in record.keys():
                        write_row.append(record[key])
                    ita_writer.writerow(write_row)
    
    with open(temp_ita_file.name, 'r+') as upload_data:
        block_blob_service.create_blob_from_text(container_name="ntto", blob_name = 'nttobeaitadata.csv', text = str(upload_data.read()))
    
    temp_ita_file.close()

    getCountries = base_api_url+'&method=getParameterValues&'+intlservtrade + "&parametername=areaorcountry"

    results_countries = r.get(getCountries)

    intl_countries = []
    for country in results_countries.json()['BEAAPI']['Results']['ParamValue']:
        intl_countries.append(country['Key'])

    intl_data = []
    intl_countries.remove('AllCountries')
    country = 'Africa'
    query = base_api_url+'method=getData&'+intlservtrade+ist_services+'&areaorcountry='+country
    write_row = []

    temp_intl_file = tempfile.NamedTemporaryFile("r+", delete=False)
    with open(temp_intl_file.name, 'w+') as intlcsvfile:
        intl_headers = r.get(query).json()['BEAAPI']['Results']['Dimensions']
        for header in intl_headers:
            write_row.append(header['Name'])
        write_row.append('Notes')
        intl_writer = csv.writer(intlcsvfile, delimiter=',', quotechar='"', quoting = csv.QUOTE_MINIMAL)
        intl_writer.writerow(write_row)
        for country in intl_countries:
            write_row = []
            query = base_api_url+'method=getData&'+intlservtrade+ist_services+'&areaorcountry='+country 
            temp_store = r.get(query).json()
            print(query)
            if 'Data' in temp_store['BEAAPI']['Results'].keys():
                intl_results = temp_store['BEAAPI']['Results']['Data']
                for record in intl_results:
                    write_row=[]
                    for key in record.keys():
                        write_row.append(record[key])
                    intl_writer.writerow(write_row)
    with open(temp_intl_file.name, 'r+') as upload_data:
        block_blob_service.create_blob_from_text(container_name="ntto", blob_name = 'nttobeaintlservtradedata.csv', text = str(upload_data.read()))
    
    temp_intl_file.close()