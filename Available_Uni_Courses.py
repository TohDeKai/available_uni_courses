# Importing essential modules
import requests
from bs4 import BeautifulSoup
'''
# A-Level Grades Conversion to UAS
grade_to_uas = {"A": 20, "B": 17.5, "C": 15, "D": 12.5, "E": 10, "S": 5, "U": 0}

# Ask user to enter their A - Levels Score
print ("Please enter your A Level Score")
h2_1 = input('What is the grade of your first H2?').upper()
h2_2 = input('What is the grade of your second H2?').upper()
h2_3 = input('What is the grade of your third H2?').upper()
gp = input('What is the grade of your General Paper?').upper()
pw = input('What is the grade of your Project Work?').upper()
h1 = input('What is the grade of your H1?').upper()

# Calculating to UAS
try:
    h2_total = grade_to_uas[h2_1] + grade_to_uas[h2_2] + grade_to_uas[h2_3]
    h1_total = (grade_to_uas[gp] + grade_to_uas[pw] + grade_to_uas[h1])/2
    total_uas = h2_total + h1_total
    print (total_uas)
except KeyError:
    print ("Only letter grades are accepted. For example, \"A\" or \"B\"")
'''
# Web - Scraping

URL = 'http://www.nus.edu.sg/oam/undergraduate-programmes/indicative-grade-profile-(igp)'
page = requests.get(URL)

soup = BeautifulSoup(page.content, 'html.parser')

results = soup.find(id="ContentPlaceHolder_contentPlaceholder_TC88F994D007_Col00")

# print(results.prettify())

igp_elems = results.find_all('tr')
for i in igp_elems:
    print(i, end='\n'*2)