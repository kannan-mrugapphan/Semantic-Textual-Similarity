from bs4 import BeautifulSoup
import requests

from datetime import datetime
import locale

source = requests.get('https://helpx.adobe.com/security/products/magento/apsb20-02.html').text

soup = BeautifulSoup(source, 'lxml')
#print(soup.prettify())

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

CVEs = []
currentCVE = {}

timestamp = datetime.utcnow().isoformat()
currentCVE['Timestamp'] = timestamp

tables = soup.findAll('div', class_ = 'table parbase section')
bulletinInfo = tables[0]
datePublished = bulletinInfo.findAll('tr')[1].findAll('td')[1].text

publishedDate = formatDate(datePublished)
currentCVE['Published Date'] = publishedDate

vulnerablityDetails = tables[3]
#print(vulnerablityDetails.prettify())
id = vulnerablityDetails.findAll('tr')[1].findAll('td')[4].text.replace(u'\xa0', u'').replace(u'\n', u'')
currentCVE['ID'] = id

url = 'https://helpx.adobe.com/security/products/magento/apsb20-02.html'
currentCVE['URL'] = url

name = soup.find('div', class_ = 'page-description').text.strip().split('|')[0].split()[-1]
currentCVE['Name'] = name

description = vulnerablityDetails.findAll('tr')[1].findAll('td')[0].text
currentCVE['Description'] = description.replace(u'\xa0', u'').replace(u'\n', u'')

cpeList = []
affectedVersions = tables[1].findAll('tr')[1:]
for version in affectedVersions:
    version = version.findAll('td')
    current = {}
    current['Vendor'] = version[0].text.split()[0]
    current['Product'] = version[0].text.replace(u'\xa0', u'').replace(u'\n', u'')
    current['Category'] = 'a'
    current['VersionEndIncluding'] = version[1].text.split()[0].replace(u'\xa0', u'').replace(u'\n', u'')
    cpeList.append(current)

currentCVE['CPE_list'] = cpeList
print(currentCVE)
