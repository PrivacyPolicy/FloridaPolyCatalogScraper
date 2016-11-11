import urllib.request
import re
import html5lib
from bs4 import BeautifulSoup

DEBUG = True;

semester = 7;
#url = 'http://floridapolytechnic.catalog.acalog.com/preview_program.php?catoid=' + str(semester) + '&poid=401&returnto=302'
url = 'file:C:/Users/Gabe/Documents/School/Etcetera/Scrapers/cache/preview_program.php&catoid=7&poid=401.html'
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

        # string = ''
        # all of this... ALL. OF. THIS. To get a nice list of prereqs
        try:
            a = soup.find_all('div', {'class': 'ajaxcourseindentfix'})[1]
            b = a.find('p') # <p> containing prereq data
            c = b.text.split('Prerequisites: ')[1] # text containing class list
            d = str(c.encode('utf-8'))[2:-1] # remove anoying weird stuff at end
            e = d.replace('\\xc2\\xa0', '').replace('\\xc3\\x82', ' - ') # rmv weird chars
            f = e.replace(', ', ' and ').replace(' and or ', ' or ').replace(' and and ', ' and ') # some use commas instead of 'and'
            g = f.replace(' AND ', ' and ').replace(' OR ', ' or ') # fix capitalization inconsistancies
            # g = class data in string form

            # string += '\n\n-' + str(id) + '-----------------------------\n\n' + prereqs

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

            prereqs = array
            # prereqs = prereq data in str(array) form


        except IndexError:
            prereqs = 'null'
            if DEBUG: print('index error for id: ' + id)
            pass # doesn't even have Prerequisites


        # if id == '3023':
        #   print(string)

        return {'id': id, 'number': number, 'name': name, 'credits': credits, 'prereqs': prereqs}


with urllib.request.urlopen(url) as response:
   html = response.read()

   soup = BeautifulSoup(html, "html.parser")

   global numberToID
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
               print(course)
       except KeyError:
           pass
   # print(numberToID)
