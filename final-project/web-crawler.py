import requests
from lxml import html
from collections import Counter

"""This program uses the requests and lxml libraries for web scrapping. 
It extracts headlines from major news outlets and compiles them"""

'''Stop words are filtered out. This list is from the Stanford NLP Group'''
stop_words = ["a", "an", "and", "how", "what", "why", "are", "as", "about", "after", "what", "at", "be", "by", "for", "from",
               "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
               "to", "was", "were", "will", "with", "i", "I", "his", "she", "him", "her", "their", "there", "where"]

def main():
    news= {'BBC':bbc(), 'NYTimes':nytimes(), 'GoogleNews':google(), 'Reuters':reuters()}
    most_headlines = max(iter(news.keys()), key=lambda k: len(news[k]))
    proper_nouns_master= {}
    
    headlines_used = {'BBC':[], 'NYTimes':[], 'GoogleNews':[], 'Reuters':[]}
 
    for current_outlet in news.keys():
        for headline in news[current_outlet]:
            headlines_used[current_outlet].append(headline)
            print(headline+" -"+current_outlet)
            kw = keywords(headline)
            pn = proper_nouns(headline)
            for name in pn:
                if name in proper_nouns_master.keys():
                    proper_nouns_master[name]+=1
            else:
                    proper_nouns_master[name]=1


            for news_outlet in news.keys():
                if news_outlet is not current_outlet:
                    for headline_1 in news[news_outlet]:
                        if headline_1 not in headlines_used[news_outlet]:
                            kw_1 = keywords(headline_1)
                            pn_1 = proper_nouns(headline_1)
                            for name in pn_1:
                                if name in proper_nouns_master.keys():
                                    proper_nouns_master[name]+=1
                                else:
                                    proper_nouns_master[name]=1
                            keywords_similarity = similarity(kw, kw_1)
                            proper_nouns_similarity = similarity(pn, pn_1)
                            if keywords_similarity>= 0.1:
                                if news_outlet is not "NYTimes" and current_outlet is not "NYTimes":
                                    if proper_nouns_similarity>= 0.3:
                                        headlines_used[news_outlet].append(headline)
                                        print(headline_1+" -"+news_outlet)
                                else: 
                                    headlines_used[news_outlet].append(headline)
                                    print(headline_1+" -"+news_outlet)
            print("\n")
            
    print("The most common terms in the news are:")
    most_common = (Counter.most_common(proper_nouns_master, 5))
    for i,j in most_common:
        print(i+" which occurs "+str(j)+" times.")
        
    







#Checks what percentage similar the contents of two sets are
def similarity(set1, set2):
    if len(set1) is 0 or len(set2) is 0:
        return 0
    intersection = set1 & set2
    if len(set1)>len(set2):
        return len(intersection)/len(set1)
    else:
        return len(intersection)/len(set2)



def unpunctuated(text):
	edited_text= text
	illegal_chars= [".", ",", "\'s", ":", ";", "\"", "\'", "?", "!", "   "] #"'s" removed before "/'"
	for i in illegal_chars:
		edited_text = edited_text.replace(i , "")    
	return edited_text


#Returns keywords in a headline
def keywords(text):
    keywords=set()
    edited_text= unpunctuated(text)
    words=set(edited_text.split())
    for word in words:
        if word not in stop_words:
            keywords.add(word)
    return keywords


#Returns proper nouns in a headline
def proper_nouns(text):
    edited_text= unpunctuated(text)
    words=set(edited_text.split())
    proper_nouns_lst = [x for x in words if x[0].isupper()]
    proper_nouns= set(proper_nouns_lst)
    pn_edited = []
    
    for noun in proper_nouns: 
        lowercase = noun.lower()
        if lowercase not in stop_words:
            pn_edited.append(noun)
    result = set(pn_edited)
    return result

#Removes indents from text extracted from the site HTML
def remove_indents(text):
	indents= ["\n", "\t", "  "]
	new_text=text
	for i in indents:
		new_text = new_text.replace(i,"")

	return new_text


#Extract Headlines from NYTimes
def nytimes():
    response = requests.get("http://www.nytimes.com")
    if (response.status_code == 200):
        pagehtml = html.fromstring(response.text)
        NYTimes = pagehtml.xpath('//article[@class="story theme-summary"]/h2[@class="story-heading"]/a/text()')
        NYTimes.append(pagehtml.xpath('//article[@class="story theme-summary lede"]/h2[@class="story-heading"]/a/text()')[0])
    return NYTimes



#Extract Headlines from GoogleNews
def google():
    response = requests.get("http://news.google.com")
    if (response.status_code == 200):     
        pagehtml = html.fromstring(response.text)
        GoogleNews = pagehtml.xpath('//h2[@class="esc-lead-article-title"] \
                                    /a/span[@class="titletext"]/text()')
    return GoogleNews

#Extract Headlines from Reuters
def reuters():
    response = requests.get("http://www.reuters.com/news/archive/topNews?view=page")
    if (response.status_code == 200):
        pagehtml = html.fromstring(response.text)
        reuters_raw= pagehtml.xpath('//h3[@class="story-title"]/text()')
        reuters=[remove_indents(x) for x in reuters_raw]
    return reuters

#Extract headlines from BBC
def bbc():
    response = requests.get("http://www.bbc.com/news")
    if (response.status_code == 200):
        pagehtml = html.fromstring(response.text)
        bbc= pagehtml.xpath('//a[@class="gs-c-promo-heading nw-o-link-split__anchor gs-o-faux-block-link__overlay-link gel-paragon-bold"]/h3[@class="gs-c-promo-heading__title gel-paragon-bold nw-o-link-split__text"]/text()')
        bbc+= pagehtml.xpath('//a[@class="gs-c-promo-heading nw-o-link-split__anchor gs-o-faux-block-link__overlay-link gel-pica-bold"]/h3[@class="gs-c-promo-heading__title gel-pica-bold nw-o-link-split__text"]/text()')
        bbc_set = set(bbc)
        return(bbc_set)

"""
#Extract Headlines from CNN [ERROR NOT WORKING]
response = requests.get("http://www.cnn.com")
if (response.status_code == 200):
	pagehtml = html.fromstring(response.text)

	CNN= pagehtml.xpath('ul[@class="cn cn-list-xs cn--idx-2 cn-container_4037A43D-2B70-57AC-A8A8-74FDC9F26490 cn--expandable cn--collapsed"]/h3[@class="cd__headline"]/a/span[@class="cd__headline-text"]/text()')
	#print(pagehtml.xpath('//*[@id="homepage1-zone-1"]/div[2]/div/div[1]/ul/article[2]/div/div/h3/a/span[1]/text()'))

print("\n".join(CNN))"""




main()