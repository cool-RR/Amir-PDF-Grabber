import sys
import os
import re
import urllib2

import BeautifulSoup as beautiful_soup_module


pdf_file_pattern = re.compile('^.*\.pdf$')
file_name_from_url_pattern = re.compile('^.*/(.*)$')


def get_file_name_from_url(url):
    return file_name_from_url_pattern.match(url).groups()[0]


def get_pdf_links_from_url(url):
    url_file = urllib2.urlopen(url)
    try:
        html_string = str(url_file.read())
    finally:
        url_file.close()
    soup = beautiful_soup_module.BeautifulSoup(html_string)
    a_tags = soup.findAll('a', attrs={'href': pdf_file_pattern})
    pdf_urls = [
        dict(a_tag.attrs)['href'] for a_tag in a_tags
    ]
    return pdf_urls


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
    urls = get_pdf_links_from_url(url)
    download_urls_to_folder(urls, folder)
    
