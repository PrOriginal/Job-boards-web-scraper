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
css_styles = [{"selector": "",
               "props": [("border-collapse", "collapse")]
               },
              {"selector": "th, td",
               "props": [("padding", "5px"), ("border", "solid 1px #777")]
               },
              {"selector": "th",
               "props": [("background-color", "lightblue")]
               }]

titles = []
job_urls = []
salaries = []
expected_tech = []
optional_tech = []


def make_clickable(val):
    """Makes clickable links for html table"""
    return "<a href='{0}'>Click the link</a>".format(val)


def parse_justjoin(url):
    """
    Finds div that contains desired elements to simplify further steps.
    Than passes it to the next function.
    """
    soup = get_html_justjoin(url)
    soup = soup.find("div", class_="css-ic7v2w")
    get_content_justjoin(soup)


def get_html_justjoin(url):
    """Uses selenium to get full html. Makes soup out of that html, and passes it to the next function"""
    options = Options()
    # Headless Mode
    options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=options)
    driver.get(url)
    # Zooms out the page to get all divs
    driver.execute_script("document.body.style.zoom='25%'")
    soup = BeautifulSoup(driver.page_source, "html.parser")
    return soup


def parse_pracuj(url):
    """ 
    Collects job offers urls, adds them to the list. Parses urls from that list.
    Adds desired job information to the relevant lists.
    """
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.content, "html.parser")

    for job_title in soup.find_all("h2", class_="b1iadbg8"):
        if job_title.find("a") != None:
            titles.append(job_title.get_text().strip())
        else:
            print(
                f"The following job offer does't contain a standard link : {job_title.get_text()}")
    for job_url in soup.find_all("a", class_="o1o6obw3 bwcfwrp njg3w7p"):
        job_urls.append(job_url.get("href"))
    i = 0
    for url in job_urls:
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print(f"ERROR :  {url}")
        soup = BeautifulSoup(r.content, "html.parser")
        # finds all required technologies and makes them into the list
        expected_tech.append([e.get_text() for e in soup.find_all(
            "li", class_="offer-viewjJiyAa offer-vieweKR6vg")])
        # Optional technologies have the same id as a required ones. To avoid duplication if statment is added
        optional_tech.append([e.get_text() for e in soup.find_all(
            "p", class_="offer-viewU0gxPf") if e.get_text() not in expected_tech[i]])
        i += 1
        salary = soup.find("strong", class_="offer-viewLdvtPw")
        if salary:
            salaries.append(unicodedata.normalize('NFKD', salary.get_text()))
        else:
            salaries.append("Undisclosed salary")


def get_content_justjoin(soup):
    """ 
    Collects job offers urls, adds them to the list. Parses urls from that list.
    Adds desired job information to the relevant lists.
    Does the similar as a get_content_pracuj. Due to the differences of the websites uses another approach in the elements search. 
    """
    a_tags = soup.find_all("a")
    # Removing unwanted element
    a_tags.pop()
    justjoin_urls = []
    for url in a_tags:
        partial_url = url.get("href")
        justjoin_urls.append("https://justjoin.it" + partial_url)
    job_urls.extend(justjoin_urls)

    for url in justjoin_urls:
        soup = get_html_justjoin(url)
        titles.append(soup.find("div", class_="css-1id4k1").get_text())
        expected = []
        optional = []
        # Sorting techs. "Nice to have" to optional_tech list, others to expected_tech list
        for div in soup.find_all("div", class_="css-1xm32e0"):
            tech = div.find("div", class_="css-1eroaug").get_text()
            lvl = div.find("div", class_="css-19mz16e").get_text()
            if lvl != "nice to have":
                optional.append(tech)
            else:
                expected.append(tech)
        expected_tech.append(expected)
        optional_tech.append(optional)

        salary = soup.find("span", class_="css-a2pcn2")
        if not salary:
            print(url)
        salaries.append(unicodedata.normalize('NFKD', salary.get_text()))


for name, url in job_boards.items():
    if name == "Pracuj.pl":
        parse_pracuj(url)
    elif name == "justjoin.it":
        parse_justjoin(url)

# Making Pandas DataFrame to visualize data in the HTML table
columns = {"Title": titles, "URL": job_urls, "Salary": salaries,
           "Expected technologies": expected_tech, "Optional technologies": optional_tech}

df = pd.DataFrame(columns)
df.index = range(1, len(df)+1)
df["Expected technologies"] = df["Expected technologies"].apply(
    ', '.join).replace("", "Not specified")
df["Optional technologies"] = df["Optional technologies"].apply(
    ', '.join).replace("", "Not specified")
df = df.style.format({'URL': make_clickable}).set_table_styles(css_styles)
html = df.to_html()
text_file = open("index.html", "w", encoding='utf-8')
text_file.write(html)
text_file.close()
