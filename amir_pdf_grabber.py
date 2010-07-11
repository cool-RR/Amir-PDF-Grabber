import sys
import os
import re
import urllib2

import BeautifulSoup as beautiful_soup_module



DEFAULT_SEMESTER = 'Spring2010'

pdf_file_pattern = re.compile('^.*\.pdf$')
file_name_from_url_pattern = re.compile('^.*/(.*)$')


def get_file_name_from_url(url):
    return file_name_from_url_pattern.match(url).groups()[0]


def get_soup_from_url(url):
    url_file = urllib2.urlopen(url)
    try:
        html_string = str(url_file.read())
    finally:
        url_file.close()
    soup = beautiful_soup_module.BeautifulSoup(html_string)
    return soup

def get_pdf_links_from_soup(soup):
    a_tags = soup.findAll('a', attrs={'href': pdf_file_pattern})
    pdf_urls = [
        dict(a_tag.attrs)['href'] for a_tag in a_tags
    ]
    return pdf_urls


def get_pdf_list_links_from_soup(soup, base_url):
    a_tags = soup.findAll(
        'a',
        attrs={
            'href': re.compile(r'^%s.*$' % 'ho_')
        }
    )
    
    pdf_list_pseudourls = [
        dict(a_tag.attrs)['href'] for a_tag in a_tags
    ]
    
    pdf_list_urls = [
        pdf_list_pseudourl \
        if pdf_list_pseudourl.startswith('http') else
        base_url.rsplit('/', 1)[0] + '/' + pdf_list_pseudourl
        
        for pdf_list_pseudourl in pdf_list_pseudourls
    ]    
    
    return pdf_list_urls 


def download_urls_to_folder(urls, folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)
    for url in urls:
        try:
            url_file = urllib2.urlopen(url)
            file_name = get_file_name_from_url(url)
            with file(os.path.join(folder, file_name), 'wb') as my_file:
                my_file.write(url_file.read())
        finally:
            url_file.close()

            
def download_pdf_links_to_folder(url, folder):
    soup = get_soup_from_url(url)
    urls = get_pdf_links_from_soup(soup)
    download_urls_to_folder(urls, folder)

    
def course_number_to_base_url(course_number, semester=DEFAULT_SEMESTER):
    return 'http://webcourse.cs.technion.ac.il/%s/%s/en/ho' % \
           (course_number, semester)


def get_all_pdf_list_urls_from_base_url(base_url):
    main_url = base_url + '.html'
    
    pdf_list_urls = set([main_url])
    uncrawled_pdf_list_urls = set([main_url])
    while uncrawled_pdf_list_urls:
        pdf_list_url = uncrawled_pdf_list_urls.pop()
        soup = get_soup_from_url(pdf_list_url)
        for child_pdf_list_url in get_pdf_list_links_from_soup(soup, base_url):
            pdf_list_urls.add(child_pdf_list_url)
            uncrawled_pdf_list_urls.add(child_pdf_list_url)
    
    return pdf_list_urls

        
def download_pdfs_recursively_for_course_number(course_number,
                                                folder=None,
                                                semester=DEFAULT_SEMESTER):
    if folder is None:
        folder = '.'
    folder = os.path.join(folder, str(course_number))
    if not os.path.isdir(folder):
        os.mkdir(folder)
    base_url = course_number_to_base_url(course_number, semester)
    pdf_list_urls = get_all_pdf_list_urls_from_base_url(base_url)
    
    for pdf_list_url in pdf_list_urls:
        
        file_name = get_file_name_from_url(pdf_list_url)
        if file_name == 'ho.html':
            little_folder = folder    
        else:
            title = file_name[3:].rsplit('.', 1)[0]
            # Cutting off '_ho' and extenstion
            little_folder = os.path.join(folder, title)
            
        download_pdf_links_to_folder(
            pdf_list_url, 
            little_folder
        )
   
        
HELP_STRING = \
r'''
Usage:

    amir_pdf_grabber.py 122435
    
    This will download PDFs for course number 122435 to folder ./122435

    
To select a specific folder, do like this:

    amir_pdf_grabber.py 122435 c:\Documents
    
    This will download PDFs for course number 122435 to folder c:\Documents\122435
'''
        
if __name__ == '__main__':
    
    try:
        course_number = int(sys.argv[1])
    except ValueError:
        if 'help' in sys.argv[1]:
            print(HELP_STRING)
            exit()
        else:
            raise Exception('%s is not a valid course number' % sys.argv[1])
    except IndexError:
        print(HELP_STRING)
        exit()
    try:
        folder = sys.argv[2]
    except IndexError:
        folder = '.'
    
    download_pdfs_recursively_for_course_number(course_number, folder) 
    
