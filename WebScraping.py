from bs4 import BeautifulSoup
import requests
from datetime import datetime
import json
import os

os.chdir('C:/ms cs/Web Scraping')

#read from a text file with a list of different webpages in seperate lines into a list
def getURLs(file):
    urlList = []
    with open(file, 'r') as f:
        for url in f:
            urlList.append(url)
    return urlList

#formatDate scraps published date from web page and converts it into iso format
def formatDate(date):
    date = date.replace(",", "")
    formatedDate = date.split()
    day = formatedDate[1]
    formatedDate[1] = formatedDate[0]
    formatedDate[0] = day
    date = ' '.join(formatedDate)
    datetimeObject = datetime.strptime(date, '%d %B %Y')
    return datetimeObject.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

def buildCVE(vulnerablity, idColumn, descriptionColumn, affectedVersion):
    timestamp = datetime.utcnow().isoformat() #current timestamp in iso format
    currentCVE['Timestamp'] = timestamp

    #observation - all the given help pages of adobe had 4 tables
    #table 1 - bulletin info with id, published date and priority
    #table 2 - affected version with product, version and platform
    #table 3 - solution with product, version and platform
    #table 4 - vulnerablity details with category and cve numbers
    tables = soup.findAll('div', class_ = 'table parbase section') #fetch all tables

    bulletinInfo = tables[0] #scrap published date and format it to iso 
    datePublished = bulletinInfo.findAll('tr')[1].findAll('td')[1].text
    publishedDate = formatDate(datePublished)
    currentCVE['Published Date'] = publishedDate

    #print(vulnerablityDetails.prettify())
    #cve id is the 5th column in vulnerablity table
    id = vulnerablity.findAll('td')[idColumn].text.replace(u'\xa0', u'').replace(u'\n', u'')
    currentCVE['ID'] = id

    url = 'https://helpx.adobe.com/security/products/magento/apsb20-02.html'
    currentCVE['URL'] = url

    #product name is obtained from page description class
    name = soup.find('div', class_ = 'page-description').text.strip().split('|')[0].split('for')[1]
    currentCVE['Name'] = name

    #category is the 1st column in vulnerablity table
    description = vulnerablity.findAll('td')[descriptionColumn].text
    currentCVE['Description'] = description.replace(u'\xa0', u'').replace(u'\n', u'')

    #info about each affected version is dumped into cpe list
    cpeList = buildCPEList(affectedVersion, tables)
    currentCVE['CPEs'] = {}
    currentCVE['CPEs']['CPE_List'] = cpeList
    CVEs.append(currentCVE.copy())
    return

def buildCPEList(affectedVersion, tables):
    cpeList = []
    if(affectedVersion == None):
        columnNames = tables[1].findAll('tr')[0].text.strip().split('\n')
        versionId = 0
        productId = 0
        for i in range(len(columnNames)):
            if("Version" in columnNames[i]):
                versionId = i
            if("Product" in columnNames[i]):
                productId = i
        affectedVersions = tables[1].findAll('tr')[1:]
        for version in affectedVersions:
            version = version.findAll('td')
            current = {}
            current['Vendor'] = version[productId].text.split()[0]
            current['Product'] = version[productId].text.replace(u'\xa0', u'').replace(u'\n', u'')
            current['Category'] = 'a'
            current['VersionEndIncluding'] = version[versionId].text.split()[0].replace(u'\xa0', u'').replace(u'\n', u'')
            cpeList.append(current)
    else:
        category = tables[3].findAll('tr')[1:]
        for row in category:
            version = row.findAll('td')[affectedVersion].text.strip().replace(u'\xa0', u'').replace(u' ', u'').split('\n')
            current = {}
            affectedVersions = tables[1].findAll('tr')[1:]
            for product in affectedVersions:
                product = product.findAll('td')
                current = {}
                current['Vendor'] = product[0].text.split()[0]
                current['Product'] = product[0].text.replace(u'\xa0', u'').replace(u'\n', u'')
            current['Category'] = 'a'
            current['VersionStartIncluding'] = version[0]
            current['VersionEndIncluding'] = version[-1]
            cpeList.append(current)
    return cpeList
        
def buildResult():
    #populate the CVE info starting from the vulnerablity table
    tables = soup.findAll('div', class_ = 'table parbase section')
    vulnerablityDetails = tables[3]
    columnNames = vulnerablityDetails.findAll('tr')[0].findAll('td')
    affectedVersion = None
    for i in range(len(columnNames)):
        if("CVE Number" in columnNames[i].text):
            idColumn = i
        if("Vulnerability Category" in columnNames[i].text):
            descriptionColumn = i
        if("Affected Versions" in columnNames[i].text):
            affectedVersion = i
    vulnerablityDetails = vulnerablityDetails.findAll('tr')[1:]
    for vulnerablity in vulnerablityDetails:
        buildCVE(vulnerablity, idColumn, descriptionColumn, affectedVersion)

    result['Source'] = URL.split('//')[-1].split('/')[0].split('.')[-2] #source is obtained from domain name of url
    result['Type'] = 'Vendor'
    result['CVEs'] = CVEs
    return

urlList = getURLs('urls.txt')
#URL = 'https://helpx.adobe.com/security/products/magento/apsb20-02.html'
#URL = 'https://helpx.adobe.com/security/products/experience-manager/apsb20-01.html'

for url in urlList:
    URL = str(url).replace(u'\n', u'')
    print(url)
    outputFileName = URL.split('/')[-1].split('.')[0] + '.txt'

    source = requests.get(URL).text
    soup = BeautifulSoup(source, 'lxml') 
    #print(soup.prettify())
    
    result = {}
    CVEs = []
    currentCVE = {}

    buildResult()

    output = json.dumps(result, indent = 4)
    print(output)
    with open(outputFileName, 'w') as f:
        f.write(output)
