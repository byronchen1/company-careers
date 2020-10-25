import selenium
from selenium import webdriver
import pandas as pd
import numpy as np

def _otpp_postings(url="https://otppb.wd3.myworkdayjobs.com/OntarioTeachers_Careers"):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.set_page_load_timeout(5)
    driver.maximize_window()
    driver.implicitly_wait(5)
    driver.set_window_position(-10000,0)

    desc=[]
    elems = driver.find_elements_by_xpath('.//li[@data-automation-id = "compositeContainer"]')
    for e in elems:
        contents = e.text.replace('\n', ' | ').split(" | ")
        for c in range(len(contents)):
            contents[c]=contents[c].strip()
        if len(contents)<4:
            contents.insert(2, np.NaN)
        contents.insert(4, "https://otppb.wd3.myworkdayjobs.com/OntarioTeachers_Careers")
        desc.append(contents)

    driver.quit()
    return desc

def _hoopp_posting(url='https://hoopp.taleo.net/careersection/ex/jobsearch.ftl'):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.set_page_load_timeout(5)
    driver.maximize_window()
    driver.implicitly_wait(5)
    driver.set_window_position(-10000,0)
    
    desc,hrefs,prefix_u=[],[],'https://hoopp.taleo.net/careersection/ex/jobdetail.ftl?job='
    
    lnks=driver.find_elements_by_tag_name("a")
    for lnk in lnks:
        if prefix_u in str(lnk.get_attribute('href')) :
            hrefs.append(str(lnk.get_attribute('href')))
    
    elems = driver.find_elements_by_xpath('.//tr[@class = "even" or @class = "odd"]')
    i=0
    for e in elems:
        contents = e.text.replace('\n', ' | ').split(" | ")
        for c in range(len(contents)):
            contents[c]=contents[c].strip()
        contents.insert(4, hrefs[i])
        i+=1
        desc.append(contents)
        
    driver.quit()
    return desc

def _cppib_postings(url="https://www.cppinvestments.com/careers/experienced-professionals"):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.set_page_load_timeout(5)
    driver.maximize_window()
    driver.implicitly_wait(5)
    driver.set_window_position(-10000,0)
    
    desc,hrefs,prefix_u=[],[],'https://jobs.smartrecruiters.com/CPPInvestments/'
    next_possible=True
    
    while next_possible:
        lnks=driver.find_elements_by_tag_name("a")
        for lnk in lnks:
            if prefix_u in str(lnk.get_attribute('href')) :
                hrefs.append(str(lnk.get_attribute('href')))
        
        elems = driver.find_elements_by_xpath('.//div[@class = "job-row row"]')
        for e in elems:
            contents = e.text.replace('\n', ' | ').split(" | ")
            for c in range(len(contents)):
                contents[c]=contents[c].strip()

            desc.append(contents)
        try:
            driver.find_element_by_xpath('.//button[@class = "action next"]').click()
        except:
            next_possible=False
    
    for i in range(len(desc)):
        desc[i].insert(4,hrefs[i])
    
    driver.quit()
    return desc

def create_dfs():
    data = _otpp_postings()
    data2 = _hoopp_posting()
    data3 = _cppib_postings()
   
    pd.set_option('display.max_colwidth', -1)
    df1 = pd.DataFrame(data,columns=['Title','ID','Location','Post Date','Link'])
    df1 = df1[~df1["Title"].str.contains("Intern") & ~df1["Title"].str.contains("New Grad")]
    df1 = df1[df1["Location"].str.contains("Canada")]
    df1 = df1[df1["Title"].str.contains("Analyst") | df1["Title"].str.contains("Associate") | df1["Title"].str.contains("Invest")]

    df2 = pd.DataFrame(data2,columns=['Title','Post Date','ID','Apply','Link'])
    df2 = df2.drop(['Apply'], axis=1)
    df2['Location'] = 'Toronto, Canada'
    df2 = df2[df2["Title"].str.contains("Analyst") | df2["Title"].str.contains("Associate") | df2["Title"].str.contains("Invest")]

    df3 = pd.DataFrame(data3,columns=['Title','ID','Department','Location','Link'])
    df3['Post Date'] = df3['Department']
    df3 = df3[df3["Location"].str.contains("Canada")]
    df3 = df3[df3["Title"].str.contains("Analyst") | df3["Title"].str.contains("Associate") | df3["Title"].str.contains("Invest")]

    df = pd.concat([df1,df2,df3],sort=True)
    return df[['Title','Post Date','Link']]

if __name__ == "__main__":
    df=create_dfs()
    f = open("postings.txt", "w")
    f.write(f"{df}")
    f.close()
