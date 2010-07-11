import urllib2
import BeautifulSoup as beautiful_soup_module

def get_pdf_links_from_url(url):
    url_file = urllib2.urlopen(url)
    try:
        html_string = str(url_file.read())
    finally:
        url_file.close()
    beautiful_soup_module.
    