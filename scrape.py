import urllib.request
import html5lib
from bs4 import BeautifulSoup
import threading
import re
import json

DEBUG = False;

global numberToID
numberToID = {}
global degrees
degrees = {}

def getCourseID(data):
    global numberToID
    a = data.split(' - ')[0] # potentially the course number
    b = a.replace(' ', '') # remove the space
    try: # have we seen this course before?
        id = numberToID[b] # yes, return the value
        return id
    except KeyError:
        return '-1' # no, this must be either junk or not a course we offer

def courseIDFromText(text): #ENC 1101 - Happy Course
    a = text.replace(' ', '', 1) #ENC1101 - Happy Course
    b = a.split(' ')[0] #ENC1101
    try:
        c = int(numberToID[b])
        return c
    except KeyError:
        return -1

def courseIndForID(courseList, id):
    for courseInd in range(0, len(courseList)):
        if str(courseList[courseInd]['id']) == str(id):
            return courseInd
    return -1

def getCourseData(semester, degree, concentration, id):
    global numberToID
    global DEBUG
    url = 'http://floridapolytechnic.catalog.acalog.com/ajax/preview_course.php?catoid=' + str(semester) + '&coid=' + id + '&display_options=a%3A2%3A%7Bs%3A8%3A~location~%3Bs%3A7%3A~program~%3Bs%3A4%3A~core~%3Bs%3A4%3A~9085~%3B%7D&show'

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

            # first of all.. does this even have prereqs???
            prereqIndic = soup.find('strong', text='Prerequisites:')
            if prereqIndic is None:
                [1][1] # throw an index error to end all this

            COMMA = 'b\', \''
            AND = 'b\'\\xc3\\x82\\xc2\\xa0and \''
            OR = 'b\'\\xc3\\x82\\xc2\\xa0or \''
            SPACE = 'b\'\\xc3\\x82\\xc2\\xa0\''

            # Testing right here y'all
            a = soup.find_all('div', {'class': 'ajaxcourseindentfix'})[1] #prereq data
            b = a.find('p') # <p> containing prereq data
            c = b.contents

            prIDs = ['2904', '3029', '3037', '3023']
            array = []
            for d in range(2, len(c) - 1):
                e = str(c[d].encode('utf-8')).lower()
                f = c[d - 2] # two elements ago; could be anded prereq <a>
                g = c[d + 1] # next element; also could be anded prereq <a>
                # if id == '2982': print('\n\n---------------------------\n:::' + e + '\n\n')
                try:
                    if e == AND or e == COMMA or e == SPACE:
                        h = courseIDFromText(f.text)
                        i = courseIDFromText(g.text)
                        if len(array) < 1: array.append(h)
                        array.append(i)
                    elif e == OR:
                        h = courseIDFromText(f.text)
                        i = courseIDFromText(g.text)
                        if len(array) < 1: array.append(h)
                        j = array[len(array) - 1] # most recently added number
                        if type(j) is int:
                            array[len(array) - 1] = [j, i]
                        elif type(j) is list:
                            array[len(array) - 1].append(i)
                except AttributeError:
                    print('That space was misleading, just keep swimming')
                    pass
            # if nothing was found, there's only one prereq
            if len(array) == 0:
                try:
                    d = b.find('a') # assumed only one link
                    e = d.text # which has the course number
                    f = courseIDFromText(e) # so extract it
                    array = [f] # and add it to the array
                except AttributeError:
                    pass
            # remove any non-provided classes in the arrays
            # also remove if it's the same as the current class
            for h in array:
                if type(h) is int:
                    if h == -1 or h == int(id):
                        array.remove(h)
                elif type(h) is list:
                    for i in h:
                        if i == -1 or i == int(id):
                            h.remove(i)
            # remove any 0-length arrays caused by above
            for i in array:
                if type(i) is list:
                    if len(i) == 0:
                        array.remove(i)
            # remove any single-element sublists caused by above operation
            for i in range(0, len(array)):
                if type(array[i]) is list:
                    if len(array[i]) == 1:
                        array[i] = array[i][0]
            prereqs = array[:]

            # t = [];
            # for j in prereqs:
            #     for k, v in numberToID.items():
            #         if v == str(j): t.append(k)
            # print(number + '\'s prereqs: ' + str(prereqs))
            # print(number + '\'s prereqs: ' + str(t))
        except IndexError:
            prereqs = []
            pass

        # Try to get all of the co-requisite data
        try:
            a = soup.find_all('div', {'class': 'ajaxcourseindentfix'})[1]
            b = a(text='Co-requisite:')[0].parent.parent # <p> containing coreq data
            b1 = b.text.replace('Co-requisite or Prerequisite:', 'Co-requisite:') # for my uses, a prereq & coreq is the same as just a coreq
            c = b1.split('Co-requisite: ')[1] # text containing course list
            d = str(c.encode('utf-8'))[2:-1] # remove anoying weird stuff at ends
            e = d.replace('\\xc2\\xa0', '').replace('\\xc3\\x82', ' - ') # rmv weird chars
            f = e.replace(', ', ' and ').replace(' and or ', ' or ').replace(' and and ', ' and ') # some use commas instead of 'and'
            g = f.replace(' AND ', ' and ').replace(' OR ', ' or ') # fix capitalization inconsistancies
            # g = course data in string form

            h = g.strip().replace(' ', '', 1) # remove first space...
            i = h.split(' ')[0] # ...which should make this the course number
            coreq = [i] # pass that because we haven't built the entire numberToID array yet
        except IndexError:
            coreq = []
            if DEBUG: print('index error for id: ' + id)
            pass # doesn't even have Co-requisites

        # only add if the class doesn't already exist
        for course in degrees[degree][concentration]:
            if course['id'] == int(id): return

        degrees[degree][concentration].append({'id': int(id), 'number': number, 'name': name, 'credits': credits, 'description': description, 'prereqs': prereqs, 'coreq': coreq, 'electivesInGroup': []})
        return

def getConcentrationData(url):
    with urllib.request.urlopen(url) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html5lib')

        # get semester from url
        semester = url.split('=')[1].split('&')[0]

        # get degree title
        for a in soup.find_all('p'): # degree in element
            try:
                b = a.a.text # degree title
            except AttributeError:
                if DEBUG: print('Not the title element; keep going')
        degree = b

        # get concentration
        a = soup.find('h1') # concentration title
        b = a.text # text
        concentration = b

        if degree not in degrees:
            degrees[degree] = {}
        degrees[degree][concentration] = []

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

                    # start a thread to load data asynchronously
                    t = threading.Thread(target=getCourseData, args=(semester,degree,concentration,f,))
                    t.start()
                    t.join()
            except KeyError:
                pass

        courseList = degrees[degree][concentration]
        # post-process
        # convert co-req temporary ids to co-req internal ids
        for course in courseList:
            try:
                course['coreq'] = [int(numberToID[course['coreq'][0]])]
            except KeyError:
                if DEBUG: print('No coreq in course ' + course['id'])
            except IndexError:
                pass # no coreqs, move on

        # find elective groups
        electiveGroups = [];
        # find all courses that say "courseA" OR "courseB" (AKA electives in my book)
        for i in soup.find_all('li', {'class': 'acalog-adhoc'}):
            if i.text.upper().strip() == 'OR':
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

        # apply electiveGroups to the courseList object
        for group in electiveGroups:
            for course in group:
                ind = courseIndForID(courseList, course)
                for addCourse in group:
                    if addCourse == course: continue
                    courseList[ind]['electivesInGroup'].append(int(addCourse))

        # remove any electives if they are also co-reqs (i.e. Chem/Chem Lab)
        for course in courseList:
            try:
                courseID = course['coreq'][0]
            except IndexError:
                continue # no coreq, so just move one
            try:
                course['electivesInGroup'].remove(courseID)
            except ValueError:
                if DEBUG: print(course['id'] + '\'s coreq (' + courseID + ') isn\'t an elective (' + str(course['electivesInGroup']) + '), but that\'s okay')

        # remove any duplicate electives
        for course in courseList:
            course['electivesInGroup'] = list(set(course['electivesInGroup']))

        degrees[degree][concentration] = courseList


# code starts running here
print('Loading...')

with open('concentrations.txt') as f:
    for line in f:
        url = line
        # start a thread to load data asynchronously
        t = threading.Thread(target=getConcentrationData, args=(url,))
        t.start()
        t.join()

# output to file
jsonData = json.dumps(degrees, indent=4)
with open('output.json', 'w') as fileObj:
    fileObj.write(jsonData)
    fileObj.close()
print('Data output to output.json')
