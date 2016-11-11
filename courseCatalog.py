import urllib.request
import re
import html5lib
from bs4 import BeautifulSoup

DEBUG = False;

semester = 7;
#url = 'http://floridapolytechnic.catalog.acalog.com/preview_program.php?catoid=' + str(semester) + '&poid=401&returnto=302'
url = 'file:C:/Users/Gabe/Documents/School/Etcetera/Scrapers/cache/preview_program.php&catoid=7&poid=401.html'
global numberToID
numberToID = {}

def fileOut(data):
    f = open('output.txt', 'w')
    f.write(str(data.encode('UTF-8')))
    f.close()
    print(str(data.encode('UTF-8')))

def arrToStr(arr):
    string = '['
    for el in arr:
        string += el + ', '
    return string[:-2] + ']'

def getClassID(data):
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
        name = b.split(' - ')[1]

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
                    theId = getClassID(c[d])
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
            b = a.find_all('p')[1] # <p> containing coreq data
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
        return {'id': id, 'number': number, 'name': name, 'credits': credits, 'prereqs': prereqs, 'coreq': coreq}


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

    # TODO convert to JSON
    print(courseList)
