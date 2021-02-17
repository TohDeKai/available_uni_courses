from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
import re

app = Flask(__name__)
URL_NUS = 'https://www.nus.edu.sg/oam/undergraduate-programmes/indicative-grade-profile-(igp)'
nus_page = requests.get(URL_NUS)
nus_soup = BeautifulSoup(nus_page.content, 'html.parser')
nus_results = nus_soup.find(id='ContentPlaceHolder_contentPlaceholder_TC88F994D007_Col00')
count = 0
grade_to_uas = {"A": 20, "B": 17.5, "C": 15, "D": 12.5, "E": 10, "S": 5, "U": 0}

def remove_html_tags(text):
    """Remove html tags from a string"""
    import re
    clean = re.compile('<.*?>')
    return re.sub(clean, '', text)

def convert_igp_to_uas(igp):
    uas = 0
    for i in igp[:3]:
        uas += grade_to_uas[i]
    uas += grade_to_uas[igp[4]]/2
    uas += 15
    return uas

nus_igp_elems = nus_results.find_all("tr", class_=False, id=False)
#Data starts from Index 3 : Faculty of Law, ends at Index 47

#SMU
#Cannot scrape:"Request unsuccessful. Incapsula incident"
#So I inspected page source, copied and pasted it into a text file instead
smu = open("SMU_IGP.txt", encoding="utf8")
smufile = smu.read()
smu_soup = BeautifulSoup(smufile, 'html.parser')
smu_results = smu_soup.find(id="content IndicativeGradeProfiles(IGP)")
smu_igp_elems = smu_results.find_all("td", class_=False, id=False)



@app.route("/",methods=['GET','POST'])
def home():
    avail_courses = []
    rankpoints = 'uncalculated'
    if request.method == 'POST':
        h21 = request.form.get('h21')
        h22 = request.form.get('h22')
        h23 = request.form.get('h23')
        h1 = request.form.get('h1')
        gp = request.form.get('gp')
        pw = request.form.get('pw')
        rankpoints = float(h21) + float(h22) + float(h23) + float(h1) + float(gp) + float(pw)
        
    for i in nus_igp_elems[3:49]:
        course = []
        course_elem = i.find('td',  class_=False, id=False)
        igp_grades = i.find('div', class_=False, id=False)
        if course_elem == None or igp_grades == None:
            continue
        else:
            if bool(re.match(r'\w{3}/\w{1}', igp_grades.text)) == False:
                continue      
            else:
                uas_for_course = convert_igp_to_uas(igp_grades.text)
                if rankpoints != 'uncalculated':
                    if float(uas_for_course) <= float(rankpoints):
                        #avail_courses.append('NUS',",",course_elem.text,",",uas_for_course) 
                        course.append('NUS')
                        course.append(course_elem.text)
                        course.append(igp_grades.text)
                        course.append(uas_for_course)
                        avail_courses.append(course)

    for i in range(len(smu_igp_elems[4:25])):
        course = []
        html_tags_removed = (remove_html_tags(str(smu_igp_elems[i+4])))
        course_name_regex =  re.search("Bachelor", html_tags_removed)
        if course_name_regex:
            course_name = (html_tags_removed)
            igp_grades = (remove_html_tags(str(smu_igp_elems[i+5])))
            uas_for_course = convert_igp_to_uas(igp_grades)
            if rankpoints != 'uncalculated':
                if float(uas_for_course) <= float(rankpoints):
                    course.append('SMU')
                    course.append(course_name)
                    course.append(igp_grades)
                    course.append(uas_for_course)
                    avail_courses.append(course)
                
    print (avail_courses)

    return render_template('home.html',rankpoints = rankpoints,avail_courses = avail_courses,URL_NUS=URL_NUS)

app.run()


             
