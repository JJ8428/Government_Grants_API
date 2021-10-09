import sys
import pandas as pd
from datetime import date, timedelta, datetime
import os
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText

args = sys.argv

# All the args to be provided
title_keyword = args[1].lower() # Do this last, due to being ineffecient
desc_keyword = args[2].lower() # Do this last, due to being ineffecient
sf_or_both = args[3].lower() # 's', 'f', 'b',  default to 'b'
# s: synopsis, f: forecast, b: both, DHEC will use b
eligibility = args[4].split('_') # 00 - 25, or 99 (as type(...) == str)
category = args[5].split('_') # ACA, AD,... or Z
agency = args[6].split('_')
weeks = int(args[7]) # 1, 2, 3, or 4 weeks
form = args[8].lower() # 'html' or 'json'
emails = args[9] # Send to the following email

# Load the data
grants_df = pd.read_pickle('tmp/clean_grants.pkl')

# Filter for synopses, forecasts, or  both
if sf_or_both == 's':
    grants_df = grants_df[grants_df['Version'].str.contains('Synopsis')]
elif sf_or_both == 'f':
    grants_df = grants_df[grants_df['Version'].str.contains('Forecast')]
elif sf_or_both == 'b':
    pass
else:
    print('Illegal arg: sf_or_both:', sf_or_both)
    sys.exit(1)

# Filter eligible applicants
possible_elgb = [
    '00',
    '01',
    '02',
    '04',
    '05',
    '06',
    '07',
    '08',
    '11',
    '12',
    '13',
    '20',
    '21',
    '21',
    '22',
    '23',
    '25',
]
if eligibility != ['99']:
    possible_grants_df = []
    for elgb in eligibility:
        if possible_elgb.__contains__(elgb):
            possible_grants_df.append(grants_df[grants_df['EligibleApplicants'].str.contains(elgb)])
    grants_df = pd.concat(possible_grants_df)
    grants_df.drop_duplicates()

# Filter by category of funding activity
possible_cat = [
    'ACA',
    'AG',
    'AR',
    'BC',
    'CD',
    'CP',
    'DPR',
    'ED',
    'ELT',
    'EN',
    'ENV',
    'FN',
    'HL',
    'HO',
    'HU',
    'ISS',
    'IS',
    'LJL',
    'NR',
    'RA',
    'RD',
    'ST',
    'O'
]
if category != ['Z']:
    possible_grants_df = []
    for cat in category:
        if possible_cat.__contains__(cat):
            possible_grants_df.append(grants_df[grants_df['CategoryOfFundingActivity'] == cat])
    grants_df = pd.concat(possible_grants_df)
    grants_df.drop_duplicates()

# Filter by agency
possible_agnc = [
    'USAID',
    'AC',
    'USDA',
    'DOC',
    'DOD',
    'ED',
    'DOE',
    'PAMS',
    'HHS',
    'DHS',
    'USDOJ',
    'DOL',
    'DOS',
    'DOI',
    'USDOT',
    'DOT',
    'VA',
    'EPA',
    'GCERC',
    'IMLS',
    'MCC',
    'NASA',
    'NARA',
    'NEA',
    'NEH',
    'NSF',
    'NRC',
    'SBA'
]
if agency != ['*']:
    possible_grants_df = []
    for agnc in agency:
        if possible_agnc.__contains__(agnc):
            possible_grants_df.append(grants_df[grants_df['AgencyCode'].str.contains(agnc)])
    grants_df = pd.concat(possible_grants_df)
    grants_df.drop_duplicates()

# Filter by weeks
today = date.today()
if [1, 2, 3, 4].__contains__(weeks):
    comp_date = today - timedelta(days=today.weekday() + (weeks*7))
    comp_date_ns = datetime(comp_date.year, comp_date.month, comp_date.day) # Convert to datetime.datetime obj
    grants_df = grants_df[grants_df['PostDate'] >= comp_date_ns]
else:
    print('Illegal arg: weeks', weeks)
    sys.exit()

# Filter for keywords
if title_keyword != 'no_filter':
    tmp_kwrds = title_keyword.split(',')
    kwrds = []
    kwrds_not = []
    for kwrd in tmp_kwrds:
        this_kwrd = kwrd.strip()
        if this_kwrd[0] != '~':
            kwrds.append(this_kwrd)
        else: # If a keyword has '~', filter out rows that have it
            kwrds_not.append(this_kwrd)
    possible_grants_df = []
    for kwrd in kwrds:
        possible_grants_df.append(grants_df[grants_df['OpportunityTitle'].str.contains(kwrd, case=False)])
    for kwrd in kwrds_not:
        possible_grants_df.append(grants_df[~grants_df['OpportunityTitle'].str.contains(kwrd, case=False)])
    grants_df = pd.concat(possible_grants_df)
    grants_df.drop_duplicates()

if desc_keyword != 'no_filter':
    tmp_kwrds = desc_keyword.split(',')
    kwrds = []
    kwrds_not = []
    for kwrd in tmp_kwrds:
        this_kwrd = kwrd.strip()
        if this_kwrd[0] != '~':
            kwrds.append(this_kwrd)
        else: # If a keyword has '~', filter out rows that have it
            kwrds_not.append(this_kwrd)
    possible_grants_df = []
    for kwrd in kwrds:
        possible_grants_df.append(grants_df[grants_df['Description'].str.contains(kwrd, case=False)])
    for kwrd in kwrds_not:
        possible_grants_df.append(grants_df[~grants_df['Description'].str.contains(kwrd, case=False)])
    grants_df = pd.concat(possible_grants_df)
    grants_df.drop_duplicates()

grants_df.to_csv('tmp/data_req.csv')

msg = EmailMessage()
msg['Subject'] = 'HHS Grants API Data Request'
msg['From'] = 'grantsapi.donotreply@gmail.com'
msg['To'] = emails
msg.set_content = 'Parameters: {sf_or_both}, {eligibility}, {weeks}'

with open('tmp/data_req.csv', 'r') as f:
    file_data = f.read()
    msg.add_attachment(file_data, filename=f.name)

with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login('grantsapi.donotreply@gmail.com', 'grantsAPI88')
    smtp.send_message(msg)