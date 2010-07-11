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
            'href': re.compile(r'^%s.*$' % base_url)
        }
    )
    pdf_list_urls = [
        dict(a_tag.attrs)['href'] for a_tag in a_tags
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
           course_number, semester


def get_all_pdf_list_urls_from_base_url(base_url):
    main_url = base_url + '.html'
    
    pdf_list_urls = set([main_url])
    uncrawled_pdf_list_urls = set([main_url])
    while uncrawled_pdf_list_urls:
        pdf_list_url = uncrawled_pdf_list_urls.pop()
        soup = get_soup_from_url(pdf_list_url)
        for child_pdf_list_url in get_pdf_list_links_from_soup(soup):
            pdf_list_url.add(child_pdf_list_url)
            uncrawled_pdf_list_urls.add(child_pdf_list_url)
    
    return pdf_list_urls

        
def download_pdfs_recursively_for_course_number(course_number,
                                                semester=DEFAULT_SEMESTER):
    base_url = course_number_to_base_url(course_number, semester)
    pdf_list_urls = get_all_pdf_list_urls_from_base_url(base_url)
    
    
        
