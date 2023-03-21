import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import unicodedata
import time

key_words = []
salaries = []
full_text = []



headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}
job_boards = {
    "Pracuj.pl": "https://www.pracuj.pl/praca/python;kw/krakow;wp?rd=30&et=17",
    "justjoin.it": "https://justjoin.it/all/all/junior?q=Python@category"
}


def parse_pracuj(soup):
    #job_divs = soup.find('div', id="c1mk5cbj")
    titles = []
    urls = []

    for job_title in soup.find_all("h2", class_ = "b1iadbg8"):
        if job_title.find("a") != None:
            titles.append(job_title.get_text().strip()) 
        else:
            print(f"The following job offer does't contain a standard link : {job_title.get_text()} ")
    
    for job_url in soup.find_all("a", {'class': "o1o6obw3 bwcfwrp njg3w7p"}):
        urls.append(job_url.get("href"))


    

    requirements = []
    optional = []
    salaries = []
    
    i = 0
    for url in urls:
        r = requests.get(url)
        #if r.status_code() == 200:
        soup = BeautifulSoup(r.content, "html.parser")
        # for item in soup.find_all("li", class_= "offer-viewjJiyAa offer-vieweKR6vg"):
        #     requirements = [item.get_text()]
        #     print(requirements)

        # finds all required technologies and makes them into the list
        requirements.append([item.get_text() for item in soup.find_all("li", class_= "offer-viewjJiyAa offer-vieweKR6vg")])
        
        # Optional technologies have the same id as a required ones. To avoid duplication if statment is added
        optional.append([item.get_text() for item in soup.find_all("p", class_= "offer-viewU0gxPf") if item.get_text() not in requirements[i]])
        
        salary = soup.find("strong", class_= "offer-viewLdvtPw")
        if salary != None:
            salaries.append(unicodedata.normalize('NFKD',salary.get_text()))
        else:
            salaries.append("Undisclosed salary")
       
        #salaries.append(unicodedata.normalize('NFKD',salary.get_text()))

        # for salary in soup.find_all("strong", class_= "offer-viewLdvtPw"):

        #     normalized_salary = unicodedata.normalize('NFKD', salary.get_text())
        #     print(normalized_salary)

        #     salaries.append([unicodedata.normalize('NFKD',item.get_text()) for item in soup.find_all("strong", class_= "offer-viewLdvtPw")])

        i+=1

    # print(titles)
    # print(urls)
    # print(len(titles))
    # print(len(salaries))    
    # print(len(requirements))
    # print(len(optional))
    # print((len(urls)))

    columns = {"Title": titles, "URL": urls, "Salary": salaries, 
            "Required_skills ": requirements, "Optional skills" : optional}


    df_analyst = pd.DataFrame(columns)

    def make_clickable(val):
        return "<a href='{0}'>{0}</a>".format(val)


    # pd.reset_option("display.max_rows", None)
    # pd.reset_option("display.max_columns", None)
    # pd.reset_option("display.width", None)
    # pd.reset_option("display.max_colwidth", -1)

    df_analyst.style.format({"URL" :make_clickable})

    print(df_analyst)

        
        

def parse_justjoin(soup):
    pass

for name, url in job_boards.items():
    page = 0
    
    r = requests.get(url, params = {"page" : page+1}, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")

    if name == "Pracuj.pl":
        parse_pracuj(soup)
    else:
        parse_justjoin(soup)
    

