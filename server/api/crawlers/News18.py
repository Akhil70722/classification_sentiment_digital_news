import requests
import xlsxwriter
from bs4 import BeautifulSoup


def News18():
    print("News 18")
    import os
    output_dir = 'data/raw'
    os.makedirs(output_dir, exist_ok=True)
    workbook=xlsxwriter.Workbook(os.path.join(output_dir, 'News18.xlsx'))
    worksheet=workbook.add_worksheet()
    row=0
    column=0
    worksheet.write(row,column,"Heading")
    worksheet.write(row,column+1,"Body")
    worksheet.write(row,column+2,"Category")
    worksheet.write(row,column+3,"URL")
    row+=1
    HEADERS = {'User-Agent': 'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148'}
    r=requests.get('https://www.news18.com', headers=HEADERS)
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
                            if(url['href'][0]=='/' and "https://www.news18.com"+url['href'] not in unique_urls.keys()):
                                unique_urls["https://www.news18.com"+url['href']]=True
                                urls_to_visit.append("https://www.news18.com"+url['href'])
                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.news18.com" and url['href'] not in unique_urls.keys()):
                                unique_urls[url['href']]=True
                                urls_to_visit.append(url['href'])
                finally:
                    continue


        while(urls_to_visit and count<20):
                urltoVisit=urls_to_visit[0]
                # Debug: print(f"Processing URL {count+1}/20: {urltoVisit}")
                urls_to_visit.pop(0)
                if(urltoVisit[0]=='h' and (["tags","tag", "livetv", "videos", "web-stories", "astrology"] not in urltoVisit.split("/"))):
                    try:
                        
                        r=requests.get(urltoVisit, headers=HEADERS)
                        if(r.status_code==200):
                            soup=BeautifulSoup(r.text, 'html.parser')
                            for url in soup.findAll('a'):
                                try:
                                    if(url.has_attr('href')):
                                        if("video" not in url['href'].split("/") and "tag" not in url['href'].split("/") and "author" not in url['href'].split("/")):
                                            if(url['href'][0]=='/' and "https://www.news18.com"+url['href'] not in unique_urls.keys()):
                                                unique_urls["https://www.news18.com"+url['href']]=True
                                                urls_to_visit.append("https://www.news18.com"+url['href'])
                                            elif(url['href'][0]=='h' and url['href'].split("/")[2]=="www.news18.com" and url['href'] not in unique_urls.keys()):
                                                unique_urls[url['href']]=True
                                                urls_to_visit.append(url['href'])
                                finally:
                                    continue
                            
                            # Find article heading - use any h1 tag (most reliable)
                            heading_title = soup.find('h1')
                            
                            # Find article content - look for article tag or any div with multiple paragraphs
                            content_div = None
                            article_tag = soup.find('article')
                            if article_tag:
                                content_div = article_tag
                            else:
                                # Find div with most paragraphs (likely article content)
                                all_divs = soup.findAll('div')
                                max_paragraphs = 0
                                for div in all_divs:
                                    paragraphs = div.findAll('p')
                                    if len(paragraphs) > max_paragraphs and len(paragraphs) >= 3:
                                        max_paragraphs = len(paragraphs)
                                        content_div = div
                            
                            # Check if we found a valid article page
                            if heading_title and content_div:
                                # Extract paragraphs from content
                                paragraphs = content_div.findAll('p')
                                # Only accept if we have at least 3 paragraphs (likely an article)
                                if len(paragraphs) >= 3:
                                    news = ""
                                    for text in paragraphs:
                                        text_content = text.text.strip()
                                        if text_content and len(text_content) > 20:  # Skip very short paragraphs
                                            news += text_content + " "
                                    
                                    # Only save if we have substantial content
                                    if len(news.strip()) > 100:
                                        heading_text = heading_title.text.strip()
                                        if heading_text and len(heading_text) > 10:
                                            worksheet.write(row, column, heading_text)
                                            worksheet.write(row, column+1, news.strip())
                                            worksheet.write(row, column+2, urltoVisit.split("/")[3] if len(urltoVisit.split("/")) > 3 else "news")
                                            worksheet.write(row, column+3, urltoVisit)
                                            
                                            row += 1
                                            count += 1
                                            print(f"  ✓ Found article {count}: {heading_text[:50]}...")
                    finally:
                        continue        
            
    finally:
        print("News18 Finished")
        workbook.close()