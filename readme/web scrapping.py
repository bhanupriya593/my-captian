Web Scraping using Python
Whenever we start a Machine Learning project, the first thing we require is a dataset to work on. While there are many sources where datasets are available, we might want to create a dataset using the data found on a website.

In this notebook, we'll explore the process to extract information from Wikipedia and form a dataset which can later be used for Data Analytics and Machine Learning applications.

Import Libraries
We'll first import all relevant libraries that we will require to access a website's HTML and extract information from the same.

import numpy as np
import pandas as pd

from urllib.request import urlopen
from bs4 import BeautifulSoup
Define functions
Firstyly, we define the function getHTMLContent, that accepts a url and uses BeautifulSoup library to get the HTML for a webpage.

def getHTMLContent(link):
    html = urlopen(link)
    soup = BeautifulSoup(html, 'html.parser')
    return soup
Understand the data
The webpage includes the information we need in the form of HTML table. Thus, we need to reach that table and extract the information. However, there might be multiple tables on the page. We would thus need to find the class of that table and then access its data.

content = getHTMLContent('https://en.wikipedia.org/wiki/List_of_countries_and_dependencies_by_population')
tables = content.find_all('table')
for table in tables:
    print(table.prettify())
The table that we will use has the class 'wikitable sortable'. It has rows of information where the first row has headings and the other rows in succession have information about each country.

Next, we explore the website for each country.

# The cell with the country name for each row includes a link to the country webpage on Wikipedia
table = content.find('table', {'class': 'wikitable sortable'})
rows = table.find_all('tr')

# List of all links
for row in rows:
    cells = row.find_all('td')
    if len(cells) > 1:
        country_link = cells[1].find('a')
        print(country_link.get('href'))
Each row has a link to the corresponding country page on Wikipedia. However, the initial weblink is missing, so we would have to append it. Let's understand the content of page with the example of one page.

def getAdditionalDetails(url):
    try:
        country_page = getHTMLContent('https://en.wikipedia.org' + url)
        table = country_page.find('table', {'class': 'infobox geography vcard'})
        additional_details = []
        read_content = False
        for tr in table.find_all('tr'):
            if (tr.get('class') == ['mergedtoprow'] and not read_content):
                link = tr.find('a')
                if (link and (link.get_text().strip() == 'Area' or
                   (link.get_text().strip() == 'GDP' and tr.find('span').get_text().strip() == '(nominal)'))):
                    read_content = True
                if (link and (link.get_text().strip() == 'Population')):
                    read_content = False
            elif ((tr.get('class') == ['mergedrow'] or tr.get('class') == ['mergedbottomrow']) and read_content):
                additional_details.append(tr.find('td').get_text().strip('\n')) 
                if (tr.find('div').get_text().strip() != '•\xa0Total area' and
                   tr.find('div').get_text().strip() != '•\xa0Total'):
                    read_content = False
        return additional_details
    except Exception as error:
        print('Error occured: {}'.format(error))
        return []
Create the dataset
Now that we have identified what all information needs to be extracted and how. We have compiled the whole process as a function above. Now, we just move across each row of the Country list and compile its data.

data_content = []
for row in rows:
    cells = row.find_all('td')
    if len(cells) > 1:
        print(cells[1].get_text())
        country_link = cells[1].find('a')
        country_info = [cell.text.strip('\n') for cell in cells]
        additional_details = getAdditionalDetails(country_link.get('href'))
        if (len(additional_details) == 4):
            country_info += additional_details
            data_content.append(country_info)

dataset = pd.DataFrame(data_content)
Now, our dataset is compiled together but lacks headers for columns. Thus, we would now add those headers and remove columns that bring no value.

# Define column headings
headers = rows[0].find_all('th')
headers = [header.get_text().strip('\n') for header in headers]
headers += ['Total Area', 'Percentage Water', 'Total Nominal GDP', 'Per Capita GDP']
dataset.columns = headers

drop_columns = ['Rank', 'Date', 'Source']
dataset.drop(drop_columns, axis = 1, inplace = True)
dataset.sample(3)

dataset.to_csv("Dataset.csv", index = False)
