import urllib.request
import re
import html5lib
from bs4 import BeautifulSoup

semester = 7;
#url = 'http://floridapolytechnic.catalog.acalog.com/preview_program.php?catoid=' + str(semester) + '&poid=401&returnto=302'
url = 'file:C:/Users/Gabe/Documents/School/Etcetera/Scrapers/cache/preview_program.php&catoid=7&poid=401.html'

def fileOut(data):
    f = open('output.txt', 'w')
    f.write(str(data.encode('UTF-8')))
    f.close()
    print(str(data.encode('UTF-8')))

def arrToStr(arr):
    string = '['
    for el in arr:
        string += str(el.encode('utf-8')) + ', '
    return string[:-2] + ']'

def getCourseData(id):
    #url = 'http://floridapolytechnic.catalog.acalog.com/ajax/preview_course.php?catoid=' + str(semester) + '&coid=' + id + '&display_options=a%3A2%3A%7Bs%3A8%3A~location~%3Bs%3A7%3A~program~%3Bs%3A4%3A~core~%3Bs%3A4%3A~9085~%3B%7D&show'
    url = 'file:C:/Users/Gabe/Documents/School/Etcetera/Scrapers/cache/preview_course.php.html&catoid=7&coid=' + id + ".html";

    with urllib.request.urlopen(url) as response:
        html = response.read()
        soup = BeautifulSoup(html, 'html5lib')

        a = soup.find('h3')
        b = a.string
        number = b.split(' - ')[0].replace(' ', '')
        name = b.split(' - ')[1]

        credits = int(soup.find('strong').next_element.next_element)

        string = ''
        try:
            a = soup.find_all('div', {'class': 'ajaxcourseindentfix'})[1]
            b = a.find('p') # <p> containing prereq data
            c = b.text.split('Prerequisites: ')[1] # text containing class list
            d = str(c.encode('utf-8'))[2:-1] # remove anoying weird stuff at end
            e = d.replace(',', ' and') # some use commas instead of and
            prereqs = e.replace('\\xc2', ' ').replace('\\xa0', ' ').replace('\\xc3', ' ').replace('\\x82', ' ') # rmv weird chars

            string += '\n\n-' + str(id) + '-----------------------------\n\n' + prereqs

            # prereqs = soup.find_all('div', {'class': 'ajaxcourseindentfix'})[1]
            # a = prereqs.text.split('Prerequisites: ')[1]
            # b = a.split('Course Description:')[0]
            # c = b.split('and')
            # for d in c:
            #     e = d.split('or')
            #     # remove if bad
            #     regex = re.compile("[a-zA-Z]{3}[0-9]{4}")
            #     filtered = filter(lambda i: not regex.search(i), e)
            #     filtered = [i for i in e if not regex.search(i)]
            #     #print(filtered)
            #     for x in filtered:
            #         #if x in e:
            #         e.remove(x)
            #     #e = e - filtered
            #
            #     if len(e) > 1: string += '['
            #     for f in range(len(e)):
            #         g = e[f].split('-')[0].strip().replace(' ', '');
            #         string += '"' + g + '"'
            #         if f < len(e) - 1: string += ', '
            #     if len(e) > 1: string += ']'
            #     if c.index(d) < len(c) - 1:
            #         string += ', '
            #     else:
            #         string += ']'
        except IndexError:
            print("index error")
            pass # doesn't even have Prerequisites
        try:
            pass
            #m = re.search(pattern, string).group(0)
        except AttributeError:
            pass
            #m = ''
        print(string)

        for i in soup.find_all('div'):
            pass
        return "hgegoieh"


with urllib.request.urlopen(url) as response:
   html = response.read()

   soup = BeautifulSoup(html, "html.parser")

   count = -5;
   for i in soup.find_all('li'):
       try:
           if i.attrs['class'][0] == 'acalog-course':
               count += 1
               if count > 5: break;
               a = i.contents[0]
               b = a.contents[0]
               c = b.attrs['onclick']
               d = c.replace(' ', '')
               e = d.split("','")[1]
               f = e.split(',')[0].split("'")[0]
            #    if f != '2904': continue
               course = getCourseData(f)
               #print(course)
       except KeyError:
           pass
