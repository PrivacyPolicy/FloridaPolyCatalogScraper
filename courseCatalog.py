import urllib.request
import re
from bs4 import BeautifulSoup

semester = 7;
url = 'http://floridapolytechnic.catalog.acalog.com/preview_program.php?catoid=' + str(semester) + '&poid=401&returnto=302'

def getCourseData(id):
    url = 'http://floridapolytechnic.catalog.acalog.com/ajax/preview_course.php?catoid=' + str(semester) + '&coid=' + id + '&display_options=a%3A2%3A%7Bs%3A8%3A~location~%3Bs%3A7%3A~program~%3Bs%3A4%3A~core~%3Bs%3A4%3A~9085~%3B%7D&show'

    with urllib.request.urlopen(url) as response:
        html = response.read()
        soup = BeautifulSoup(html, "html.parser")

        a = soup.find('h3')
        b = a.string
        number = b.split(' - ')[0].replace(' ', '')
        name = b.split(' - ')[1]

        credits = int(soup.find('strong').next_element.next_element)

        string = '['
        try:
            prereqs = soup.find_all('div', {'class': 'ajaxcourseindentfix'})[1]
            print(soup)
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
            string = '[]'
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

   for i in soup.find_all('li'):
       try:
           if i.attrs['class'][0] == 'acalog-course':
               a = i.contents[0]
               b = a.contents[0]
               c = b.attrs['onclick']
               d = c.replace(' ', '')
               e = d.split("','")[1]
               f = e.split(',')[0].split("'")[0]
               print(i.a);
               if f != '2049': continue
               course = getCourseData(f)
               #print(course)
       except KeyError:
           pass
