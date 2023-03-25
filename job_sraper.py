import requests
from bs4 import BeautifulSoup
import unicodedata
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}
job_boards = {
    "Pracuj.pl": "https://www.pracuj.pl/praca/python;kw/krakow;wp?rd=30&et=17",
    "justjoin.it": "https://justjoin.it/all/all/junior?q=Python@category"
}
  
titles = []
job_urls = []
salaries = []
expected_tech = []
optional_tech = []

def make_clickable(val):
    return "<a href='{0}'>{0}</a>".format(val)

def parse_pracuj(url):
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")
    get_content_pracuj(soup)

def parse_justjoin(url):
    soup = get_html_justjoin(url)
    soup = soup.find("div", class_= "css-ic7v2w")
    get_content_justjoin(soup)

def get_html_justjoin(url):
    options = Options()
    #Headless Mode
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    # Zooms out the page to get all divs
    driver.execute_script("document.body.style.zoom='25%'")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup

def get_content_pracuj(soup):
    for job_title in soup.find_all("h2", class_ = "b1iadbg8"):
        if job_title.find("a") != None:
            titles.append(job_title.get_text().strip()) 
        else:
            print(f"The following job offer does't contain a standard link : {job_title.get_text()}")
    
    for job_url in soup.find_all("a", class_= "o1o6obw3 bwcfwrp njg3w7p"):
        job_urls.append(job_url.get("href"))

    i= 0
    for url in job_urls:
        r = requests.get(url, headers=headers)
        #if r.status_code() == 200:
        soup = BeautifulSoup(r.content, "html.parser")

        # finds all required technologies and makes them into the list
        expected =[e.get_text() for e in soup.find_all("li", class_= "offer-viewjJiyAa offer-vieweKR6vg")]
        
        if expected:
            expected_tech.append(expected)
        else:
            expected_tech.append("Not specified")    

        # Optional technologies have the same id as a required ones. To avoid duplication if statment is added
        optional= [e.get_text() for e in soup.find_all("p", class_= "offer-viewU0gxPf") if e.get_text() not in expected_tech[i]]
        i+=1
        
        if optional:
            optional_tech.append(optional)
        else:
            optional_tech.append("Not specified") 

        salary = soup.find("strong", class_= "offer-viewLdvtPw")
        if salary:
            salaries.append(unicodedata.normalize('NFKD',salary.get_text()))
        else:
            salaries.append("Undisclosed salary")

def get_content_justjoin(soup):
    for job_title in soup.find_all("div", class_="jss244"):
        titles.append(job_title.get_text())

    #Removing unwanted element
    a_tags = soup.find_all("a")
    a_tags.pop()

    justjoin_urls = []

    for url in a_tags:
        partial_url = url.get("href")
        justjoin_urls.append("https://justjoin.it" + partial_url)

    job_urls.extend(justjoin_urls)
    
    for url in justjoin_urls:
        soup = get_html_justjoin(url)
        expected = []
        optional = []
        # Sorting techs. "Nice to have" to optional_tech list, others to expected_tech list
        for div in soup.find_all("div", class_="css-1xm32e0"):
            tech = div.find("div", class_= "css-1eroaug").get_text()
            lvl = div.find("div", class_="css-19mz16e").get_text()
            if lvl != "nice to have":
                optional.append(tech)
            else:
                expected.append(tech)

        if expected:        
            expected_tech.append(expected)
        else:
            expected_tech.append("Not specified")
        if optional:
            optional_tech.append(optional)
        else:
            optional_tech.append("Not specified")

        salary = soup.find("span", class_="css-a2pcn2")
        salaries.append(unicodedata.normalize('NFKD', salary.get_text()))

for name, url in job_boards.items():
    if name == "Pracuj.pl":
        parse_pracuj(url)
    elif name == "justjoin.it":
        parse_justjoin(url)  

columns = {"Title": titles, "URL": job_urls, "Salary": salaries, 
        "Expected technologies": expected_tech, "Optional technologies" : optional_tech}

df = pd.DataFrame(columns)
html = df.style.format({"URL" :make_clickable}).to_html()
text_file = open("index.html", "w", encoding='utf-8')
text_file.write(html)
text_file.close()
