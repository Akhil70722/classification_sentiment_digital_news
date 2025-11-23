import requests
import xlsxwriter
from bs4 import BeautifulSoup

def IndiaToday():
    print("India Today")
    import os
    output_dir = 'data/raw'
    os.makedirs(output_dir, exist_ok=True)
    workbook=xlsxwriter.Workbook(os.path.join(output_dir, 'IndiaToday.xlsx'))
    worksheet=workbook.add_worksheet()
    row=0
    column=0
    worksheet.write(row,column,"Heading")
    worksheet.write(row,column+1,"Body")
    worksheet.write(row,column+2,"Category")
    worksheet.write(row,column+3,"URL")
    row+=1
    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    r=requests.get('https://www.indiatoday.in', headers=HEADERS)
    urls_to_visit=[]
    unique_urls={}
    count=0
    try:
        if(r.status_code==200):
            soup=BeautifulSoup(r.text, 'html.parser')
            for url in soup.findAll('a'):
                try:
                    if(url.has_attr('href')):
                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                            if(url['href'][0]=='/' and "https://www.indiatoday.in"+url['href'] not in unique_urls.keys()):
                                unique_urls["https://www.indiatoday.in"+url['href']]=True
                                urls_to_visit.append("https://www.indiatoday.in"+url['href'])
                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.indiatoday.in" and url['href'] not in unique_urls.keys()):
                                unique_urls[url['href']]=True
                                urls_to_visit.append(url['href'])
                finally:
                    continue
        while(urls_to_visit and count<20):
                urltoVisit=urls_to_visit[0]
                urls_to_visit.pop(0)
            
                if(urltoVisit[0]=='h' and (["tags","tag", "livetv", "video"] not in urltoVisit.split("/"))):
                    try:
                        r=requests.get(urltoVisit, headers=HEADERS, timeout=10)
                        if(r.status_code==200):
                            soup=BeautifulSoup(r.text, 'html.parser')
                        
                            for url in soup.findAll('a'):
                                try:
                                    if(url.has_attr('href')):
                                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                                            if(url['href'][0]=='/' and "https://www.indiatoday.in"+url['href'] not in unique_urls.keys()):
                                                unique_urls["https://www.indiatoday.in"+url['href']]=True
                                                urls_to_visit.append("https://www.indiatoday.in"+url['href'])
                                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.indiatoday.in" and url['href'] not in unique_urls.keys()):
                                                unique_urls[url['href']]=True
                                                urls_to_visit.append(url['href'])
                                finally:
                                    continue
                            
                            # Find article heading - use any h1 tag
                            heading_title = soup.find('h1')
                            
                            # Find article content - look for article tag or div with most paragraphs
                            content_div = None
                            article_tag = soup.find('article')
                            if article_tag:
                                content_div = article_tag
                            else:
                                all_divs = soup.findAll('div')
                                max_paragraphs = 0
                                for div in all_divs:
                                    paragraphs = div.findAll('p')
                                    if len(paragraphs) > max_paragraphs and len(paragraphs) >= 3:
                                        max_paragraphs = len(paragraphs)
                                        content_div = div
                            
                            if heading_title and content_div:
                                paragraphs = content_div.findAll('p')
                                if len(paragraphs) >= 3:
                                    news = ""
                                    for text in paragraphs:
                                        text_content = text.text.strip()
                                        if text_content and len(text_content) > 20:
                                            news += text_content + " "
                                    
                                    if len(news.strip()) > 100:
                                        heading_text = heading_title.text.strip()
                                        if heading_text and len(heading_text) > 10:
                                            category = urltoVisit.split("/")[3] if len(urltoVisit.split("/")) > 3 and urltoVisit.split("/")[3] != 'cities' else "india"
                                            
                                            worksheet.write(row, column, heading_text)
                                            worksheet.write(row, column+1, news.strip())
                                            worksheet.write(row, column+2, category)
                                            worksheet.write(row, column+3, urltoVisit)
                                        
                                            row += 1
                                            count += 1
                                            print(f"  ✓ Found article {count}: {heading_text[:50]}...")
                    except Exception as e:
                        continue
                    finally:
                        continue        
            
        
    finally:
        print("India today finished")
        workbook.close()
    