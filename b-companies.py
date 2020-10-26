import selenium
from selenium import webdriver
import pandas as pd
import time

def _td(url="https://jobs.td.com/en-CA/job-search-results/?location=Toronto%2C%20ON%2C%20Canada&latitude=43.653226&longitude=-79.3831843&radius=1"):
    driver = webdriver.Chrome()
    driver.get(url)
    driver.set_page_load_timeout(5)
    driver.maximize_window()
    driver.implicitly_wait(5)
    driver.set_window_position(-10000,0)
    
    desc,hrefs,prefix_u=[],[],'/en-CA/jobs/'
    next_possible=True

    while next_possible:
        lnks=driver.find_elements_by_tag_name("a")
        for lnk in lnks:
            if prefix_u in str(lnk.get_attribute('href')) :
                hrefs.append(str(lnk.get_attribute('href')))
            
        elems = driver.find_elements_by_xpath('.//ul[@class = "job-innerwrap"]')
        for e in elems:
            contents = e.text.replace('\n', ' | ').split(" | ")
            for c in range(len(contents)):
                contents[c]=contents[c].strip()

            desc.append(contents)
        try:
            next_btn = driver.find_element_by_xpath('.//a[@onclick = "CWS.jobs.next_page(); return false;"]')
            driver.execute_script("arguments[0].scrollIntoView();", next_btn)
            next_btn.click()
            time.sleep(1)
        except:
            next_possible=False
    
    for i in range(len(desc)):
        desc[i].insert(4,hrefs[i])
    
    driver.quit()
    return desc
    
    
def td_df():
    data=_td()

    pd.set_option('display.max_colwidth', -1)
    td_df = pd.DataFrame(data)
    td_df.dropna(axis='columns',inplace=True)
    td_df.rename(columns={0: "Title", 1: "Division", 2: "Location", 3: "Post Date", 4: "Link"}, inplace=True)

    td_df = td_df[~td_df["Title"].str.contains("Intern") & ~td_df["Title"].str.contains("New Grad") &  ~td_df["Division"].str.contains("Campus Program")]
    td_df = td_df[td_df["Location"].str.contains("Toronto")]
    td_df = td_df[td_df["Title"].str.contains("Analyst") | td_df["Title"].str.contains("Associate") | td_df["Title"].str.contains("Invest") | td_df["Title"].str.contains("Manage")]
    return td_df
    
    
if __name__ == "__main__":
    df=td_df()
    df.to_csv("postings_3.csv",index=False)
