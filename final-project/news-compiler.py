from bs4 import BeautifulSoup
import requests
import urllib3
from lxml import html


from bs4 import BeautifulSoup
import requests
import urllib3
from lxml import html

#extract headlines- SAMPLE from google news

site_url = input("What is your website? ")
response = requests.get(site_url)
if (response.status_code == 200):
	pagehtml = html.fromstring(response.text)

	news = pagehtml.xpath('//h2[@class="esc-lead-article-title"] \
                          /a/span[@class="titletext"]/text()')

print("\n".join(news))
