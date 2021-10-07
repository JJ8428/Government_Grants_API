from datetime import date, datetime
import os
import pandas as pd
import requests
import sys
import xml.etree.ElementTree as ET
import zipfile

def download_grants_file():

    # Generating link of zipfile
    today = date.today().strftime('%Y%m%d')
    link_head = 'https://www.grants.gov/extract/GrantsDBExtract'
    url = link_head + today + 'v2.zip'
    dest = 'tmp'

    # Downloading the zip file
    filename = url.split('/')[-1].replace(' ', '_')
    filepath = os.path.join(dest, filename)
    r = requests.get(url, stream=True)
    if r.ok:
        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                    if chunk:
                        f.write(chunk)
                        f.flush()
                        os.fsync(f.fileno())
    else:
        print('Unable to connect to grants.gov')
        print('Failed connection URL:', url)
        sys.exit()

    # Unzipping download
    zippath = dest + '/' + filename
    with zipfile.ZipFile(zippath, 'r') as zip_ref:
        zip_ref.extractall(dest)
    
    # Deleting zipped download
    os.remove(zippath)

    # Parsing the XML as a list and correcting poor format
    xml_list = []
    f = open(dest + '/' + filename.replace('.zip', '.xml'))
    for line in f.readlines():
        line = line.replace('\n', '')
        if line.__contains__('<Grants'):
            line = '<Grants>'
        xml_list.append(line)
    xml_str = '\n'.join(xml_list)
    xml = ET.fromstring(xml_str)

    # Init a pd df
    grants_df = pd.DataFrame()

    # OPPORTUNITY NUMBER,OPPORTUNITY TITLE,AGENCY CODE,AGENCY NAME,ESTIMATED FUNDING
    # EXPECTED NUMBER OF AWARDS,GRANTOR CONTACT,AGENCY CONTACT PHONE,AGENCY CONTACT EMAIL
    # ESTIMATED POST DATE,ESTIMATED APPLICATION DUE DATE,POSTED DATE,CLOSE DATE,VERSION,
    # LOI DUE DATE,AWARD FLOOR,AWARD CEILING,GRANT LENGTH (YEARS),PURPOSE

    cols = [
        'OpportunityNumber',
        'OpportunityTitle',
        'OpportunityCategory',
        'FundingInstrumentType',
        'CategoryOfFundingActivity',
        'EligibleApplicants',
        'AgencyCode',
        'AgencyName',
        'PostDate',
        'CloseDate',
        'AwardCeiling',
        'AwardFloor',
        'EstimatedTotalProgramFunding',
        'ExpectedNumberOfAwards',
        'Description',
        'Version',
        'GrantorContactEmail',
        'GrantorContactEmailDescription',
    ]

    for col in cols:
        grants_df[col] = ''

    # Filtering columns for grants that happens this year and last year
    this_year = str(date.today().year)
    last_year = str(date.today().year-1)
    years = [this_year, last_year]
    for opp in xml:
        this_opp = dict.fromkeys(cols)
        applicants = []
        for detail in opp:
            if detail.tag != 'EligibleApplicants':
                if cols.__contains__(detail.tag):
                    this_opp[detail.tag] = detail.text
            else:
                applicants.append(detail.text)
        this_opp['EligibleApplicants'] = '_'.join(applicants)
        if years.__contains__(this_opp['PostDate'][-4:]):
            grants_df = grants_df.append(this_opp, ignore_index=True)

    # Convert column to datetime[ns] type
    def convert_date(row):
        this_date = row['PostDate']
        this_year = int(this_date[-4:])
        this_day = int(this_date[2:4])
        this_month = int(this_date[0:2])
        row['PostDate'] = datetime(this_year, this_month, this_day)
        return row
    
    grants_df = grants_df.apply(lambda row: convert_date(row), axis=1)

    # Removing the xml
    os.remove(dest + '/' + filename.replace('.zip', '.xml'))

    # Save to pickle file
    grants_df.to_pickle(dest + '/clean_grants.pkl')

download_grants_file()