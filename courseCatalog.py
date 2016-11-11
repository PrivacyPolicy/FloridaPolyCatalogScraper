import urllib.request
import re
import html5lib
from bs4 import BeautifulSoup
import json

DEBUG = False;

semester = 7;
#url = 'http://floridapolytechnic.catalog.acalog.com/preview_program.php?catoid=' + str(semester) + '&poid=401&returnto=302'
url = 'file:C:/Users/Gabe/Documents/School/Etcetera/Scrapers/cache/preview_program.php&catoid=7&poid=401.html'
global numberToID
numberToID = {}

def arrToStr(arr):
    string = '['
    for el in arr:
        string += el + ', '
    return string[:-2] + ']'

def getCourseID(data):
    global numberToID
    a = data.split(' - ')[0] # potentially the course number
    b = a.replace(' ', '') # remove the space
    try: # have we seen this class before?
        id = numberToID[b] # yes, return the value
        # id += ' (' + b + ')'
        return id
    except KeyError:
        # print('(' + data + ')')
        return '-1' # no, this must be either junk or not a class we offer

def courseIndForID(courses, id):
    for courseInd in range(0, len(courses)):
        if courses[courseInd]['id'] == id:
            return courseInd
    return -1

def getCourseData(id):
    global numberToID
    global DEBUG
    #url = 'http://floridapolytechnic.catalog.acalog.com/ajax/preview_course.php?catoid=' + str(semester) + '&coid=' + id + '&display_options=a%3A2%3A%7Bs%3A8%3A~location~%3Bs%3A7%3A~program~%3Bs%3A4%3A~core~%3Bs%3A4%3A~9085~%3B%7D&show'
    url = 'file:C:/Users/Gabe/Documents/School/Etcetera/Scrapers/cache/preview_course.php.html&catoid=7&coid=' + id + ".html";

    with urllib.request.urlopen(url) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html5lib')

        a = soup.find('h3')
        b = a.string
        number = b.split(' - ')[0].replace(' ', '')
        numberToID[number] = id
        name = b.split(' - ')[1].strip()

        a = soup(text='Course Description:')[0].parent.parent # description and title
        b = a.text.split('Course Description:')[1] # remove the title
        c = str(b.encode('utf-8'))[2:-1] # convert to string, remove ends
        d = c.replace('\\xc2\\xa0', '').replace('\\xc3\\x82', ' ') # rmv weird chars
        e = d.replace('\\xe2\\x80\\x99', '\'').strip() # rmv weird chars
        description = e

        credits = int(soup.find('strong').next_element.next_element)

        # all of this... ALL. OF. THIS. To get a nice list of prereqs
        try:
            a = soup.find_all('div', {'class': 'ajaxcourseindentfix'})[1]
            b = a.find('p') # <p> containing prereq data
            c = b.text.split('Prerequisites: ')[1] # text containing class list
            d = str(c.encode('utf-8'))[2:-1] # remove anoying weird stuff at ends
            e = d.replace('\\xc2\\xa0', '').replace('\\xc3\\x82', ' - ') # rmv weird chars
            f = e.replace(', ', ' and ').replace(' and or ', ' or ').replace(' and and ', ' and ') # some use commas instead of 'and'
            g = f.replace(' AND ', ' and ').replace(' OR ', ' or ') # fix capitalization inconsistancies
            # g = class data in string form

            a = g.split(' and ') # each of the potential courses
            array = '['
            for b in a:
                c = b.split(' or ') # occasionally, you have to deal with 'or'
                if len(c) > 1: array += '['
                for d in range(0, len(c)): # each of the classes, either AND or OR
                    theId = getCourseID(c[d])
                    if theId != '-1':
                        array += theId + ', '
                if len(c) > 1: array = array[:-2] + '], '
            array = array[:-2] + ']'
            array = array.replace(',]', '')
            array = array.replace('], ', '[')
            try:
                while array[0] == ']':
                    array = array[1]
            except IndexError:
                array = ''
            if array == '':
                array = 'null'

            prereqs = array # prereqs = prereq data in str(array) form
        except IndexError:
            prereqs = 'null'
            if DEBUG: print('index error for id: ' + id)
            pass # doesn't even have Prerequisites


        # Try to get all of the co-requisite data
        try:
            a = soup.find_all('div', {'class': 'ajaxcourseindentfix'})[1]
            b = a(text='Co-requisite:')[0].parent.parent # <p> containing coreq data
            b1 = b.text.replace('Co-requisite or Prerequisite:', 'Co-requisite:') # for my uses, a prereq & coreq is the same as just a coreq
            c = b1.split('Co-requisite: ')[1] # text containing class list
            d = str(c.encode('utf-8'))[2:-1] # remove anoying weird stuff at ends
            e = d.replace('\\xc2\\xa0', '').replace('\\xc3\\x82', ' - ') # rmv weird chars
            f = e.replace(', ', ' and ').replace(' and or ', ' or ').replace(' and and ', ' and ') # some use commas instead of 'and'
            g = f.replace(' AND ', ' and ').replace(' OR ', ' or ') # fix capitalization inconsistancies
            # g = class data in string form

            h = g.strip().replace(' ', '', 1) # remove first space...
            i = h.split(' ')[0] # ...which should make this the course number
            coreq = i # pass that because we haven't built the entire numberToID array yet
        except IndexError:
            coreq = 'null'
            if DEBUG: print('index error for id: ' + id)
            pass # doesn't even have Co-requisites


        # if coreq == 'null': return '0'
        return {'id': id, 'number': number, 'name': name, 'credits': credits, 'description': description, 'prereqs': prereqs, 'coreq': coreq, 'electivesInGroup': []}


with urllib.request.urlopen(url) as response:
    html = response.read()

    soup = BeautifulSoup(html, "html.parser")

    courseList = [];
    # build course list
    for i in soup.find_all('li'):
        try:
            if i.attrs['class'][0] == 'acalog-course':
                a = i.contents[0]
                b = a.contents[0]
                c = b.attrs['onclick']
                d = c.replace(' ', '')
                e = d.split("','")[1]
                f = e.split(',')[0].split("'")[0]
                course = getCourseData(f)
                if course != 0: courseList.append(course)
        except KeyError:
            pass

    # convert coreq temp ids to coreq internal ids
    for course in courseList:
        try:
            course['coreq'] = numberToID[course['coreq']]
        except KeyError:
            if DEBUG: print('No coreq in course ' + course['id'])
            pass #

    # find elective groups
    electiveGroups = [];
    # find all courses that say "courseA" OR "courseB" (AKA electives in my book)
    for i in soup.find_all('li', {'class': 'acalog-adhoc acalog-adhoc-after'}):
        if i.strong.text.upper() == 'OR':
            a = i.previous_element.previous_element.previous_element.previous_element.previous_element.previous_element;
            b = i.next_element.next_element.next_element.next_element.next_element;
            group = [str(a).split("'")[3], str(b).split("'")[3]]
            electiveGroups.append(group)
    # find all courses that are in an HTML element grouping
    for i in soup.find_all('div', {'class': 'acalog-core'}):
        group = []
        try:
            a = i.h4.parent.find('ul')
            b = str(a).split('showCourse') # logically close to each course id
            for c in b:
                try:
                    d = c.split("'")[3] # the id (Staples: that was easy)
                    group.append(d)
                except IndexError:
                    if DEBUG: print('This was junk data: ' + c)
        except AttributeError:
            if DEBUG: print('Not a group; move on')
        if len(group) > 0:
            electiveGroups.append(group)
    # print(electiveGroups)

    # apply electiveGroups to the courseList object
    for group in electiveGroups:
        for course in group:
            ind = courseIndForID(courseList, course)
            for addCourse in group:
                if addCourse == course: continue
                courseList[ind]['electivesInGroup'].append(addCourse)

    # remove any electives if they are also co-reqs (i.e. Chem/Chem Lab)
    for course in courseList:
        courseID = course['coreq']
        try:
            course['electivesInGroup'].remove(courseID)
        except ValueError:
            if DEBUG: print(course['id'] + '\'s coreq (' + courseID + ') isn\'t an elective (' + str(course['electivesInGroup']) + '), but that\'s okay')

    # for l in courseList:
    #     print('----------\n' + str(l))

    # convert to JSON
    out = '[\n'
    space = ',\n        '
    for course in courseList:
        out += '    {\n        '
        out += '"id": ' + course['id'] + space
        out += '"number": "' + course['number'] + '"' + space
        out += '"name": "' + course['name'] + '"' + space
        out += '"credits": ' + str(course['credits']) + space
        out += '"description": "' + course['description'] + '"' + space
        out += '"prereqs": '
        if course['prereqs'] == 'null':
            out += '[]'
        else:
            out += course['prereqs']
        out += space
        out += '"coreqs": ['
        if course['coreq'] != 'null':
            out += course['coreq']
        out += ']' + space
        out += '"electivesInGroup": ['
        for elective in course['electivesInGroup']:
            out += elective + ', '
        if len(course['electivesInGroup']) > 0:
            out = out[:-2]
        out += ']'
        out += '\n    },\n'
    if len(courseList) > 0:
        out = out[:-2]
    out += '\n]\n'

    # output to file
    with open('output.json', 'w') as fileObj:
        fileObj.write(out)
        fileObj.close()

    print('Data output to output.json')

#TODO threading
