import re
import yaml
from yaml.loader import SafeLoader
import PySimpleGUI as sg
import time
import pandas as pd
import numpy as np
import os.path
import datetime
import pyautogui as p 
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
import csv
from pathlib import Path

options = Options()
options.add_experimental_option('detach', True)
username = os.getlogin( )
try:
    options.add_argument(r"--user-data-dir=C:\Users\{}\AppData\Local\Google\Chrome\User Data\Default".format(username))
except:
    pass
options.add_argument("--start-maximized")
driver = webdriver.Chrome(chrome_options=options)
# website login url 
url = 'https://www.linkedin.com/jobs/'


def main():
    yaml_init()
    log_in()
    browse_through_jobs()
    


def write_to_excel():
    filename = r"LinkedIn Applications ({}).csv".format(datetime.datetime.now().strftime("%m-%d-%Y"))
    filePath = r'{}\{}'.format(job_details_folder, filename)
    
    # CSV components
    jobLink = '.jobs-unified-top-card__content--two-pane [href]'
    jobTitle = '.jobs-unified-top-card__content--two-pane .jobs-unified-top-card__job-title'
    company = '.jobs-unified-top-card__company-name'
    location = '.jobs-unified-top-card__subtitle-primary-grouping .jobs-unified-top-card__bullet'
    recruiterName = '.hirer-card__hirer-information .app-aware-link .jobs-poster__name strong' 
    recruiterLink = '.hirer-card__hirer-information .app-aware-link' 
    
    jobLinkHref = driver.find_element(By.CSS_SELECTOR, jobLink).get_attribute('href')
    jobTitleText = driver.find_element(By.CSS_SELECTOR, jobTitle).text
    companyText = driver.find_element(By.CSS_SELECTOR, company).text
    locationText = driver.find_element(By.CSS_SELECTOR, location).text 
    try: 
        recruiterText = driver.find_element(By.CSS_SELECTOR, recruiterName).text
        recruiterHref = driver.find_element(By.CSS_SELECTOR, recruiterLink).get_attribute("href")
    except:
        recruiterText = ""
        recruiterHref = ""
    
    # Writing header for new file if the file doesnt exist
    if os.path.isfile(filePath) == 'False':
        df = pd.DataFrame({'Job Title': ['JOB TITLE'], 'Company':['COMPANY'], 'Location': ['LOCATION'], 'Link': ['LINK'], 'Recruiter': ['RECRUITER']}) 
        df.to_csv(filePath, mode='w', index = False, header=None)
    
    # Appending into the file     
    df = pd.DataFrame({'Job Title': [jobTitleText], 'Company':[companyText], 'Location': [locationText], 'Link': [jobLinkHref], 'Recruiter': [recruiterText + ' | ' + recruiterHref]}) 
    df.to_csv(filePath, mode='a',index = False, header=None)
  
        
def next_page():
    pages = '.artdeco-pagination__indicator'
    current_page_loc = '[aria-current="true"]'
    
    current_page = driver.find_element(By.CSS_SELECTOR, current_page_loc).text
    totalPages = driver.find_elements(By.CSS_SELECTOR, pages)[-1].text
    for page in range(int(current_page) + 1, int(totalPages)):
        driver.find_element(By.CSS_SELECTOR, '[aria-label="Page {}"]'.format(page)).click()
        browse_through_jobs()
        

def yaml_init():
    cwd = os.getcwd()
    with open(r'{}\linkedin-bot-new\config.yml'.format(cwd)) as f:  
        data = yaml.load(f, Loader=SafeLoader)
        global username, password, phone_number, position, location, resume_folder, job_details_folder
        
        username = "".join(data["username"])
        password = "".join(data["password"])
        phone_number = "".join(data["phone_number"])
        position = "".join(data["position"])
        location = "".join(data["location"])
        resume_folder = "".join(data["resume_folder"])
        job_details_folder = "".join(data["job_details_folder"])

        
def log_in():
    # sg.theme('SandyBeach')     
    # layout = [
    #     [sg.Text('Please enter the below')],
    #     [sg.Text('Username', size =(15, 2)), sg.InputText()],
    #     [sg.Text('Password', size =(15, 2)), sg.InputText()],
    #     [sg.Text('Search by title, skill, or company', size =(15, 2)), sg.InputText()],
    #     [sg.Text('City, state, or zip code', size =(15, 2)), sg.InputText()],
    #     [sg.Submit(), sg.Cancel()]
    # ]
      
    # window = sg.Window('Simple data entry window', layout)
    # event, values = window.read()
    # window.close()
    
    # username = values[0]
    # password = values[1]
    # job_title =  values[2]
    # location = values[3]
    
    driver.get(url)
     
    try: 
        driver.find_element("id", "session_key").send_keys(username)
        driver.find_element("id", "session_password").send_keys(password)
        driver.find_element("id", "session_password").send_keys(Keys.RETURN)
        
    except NoSuchElementException:
        pass

    WebDriverWait(driver,20).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.jobs-search-box__text-input')))[0]
    driver.find_elements(By.CSS_SELECTOR, '.jobs-search-box__text-input')[0].send_keys(position)

    WebDriverWait(driver,20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, '[aria-label="City, state, or zip code"]')))[0]
    driver.find_elements(By.CSS_SELECTOR, '[aria-label="City, state, or zip code"]')[0].send_keys(location)
    time.sleep(0.5)
    driver.find_elements(By.CSS_SELECTOR, '[aria-label="City, state, or zip code"]')[0].send_keys(Keys.RETURN)
    
    WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CSS_SELECTOR, '[aria-label="Easy Apply filter."]'))).click()

def browse_through_jobs():
    global jobs, job_list, job
    
    jobLoadTest = '.job-flavors__label'
    jobs = 'li.jobs-search-results__list-item' # Loop through all elements
    
    time.sleep(1)
    WebDriverWait(driver,20).until(EC.visibility_of_all_elements_located((By.CSS_SELECTOR, jobLoadTest)))

    ignored_exceptions=(NoSuchElementException,StaleElementReferenceException,)
    job_list = WebDriverWait(driver, 20, ignored_exceptions=ignored_exceptions).until(
        EC.visibility_of_all_elements_located((By.CSS_SELECTOR, jobs)))
    job_list = driver.find_elements(By.CSS_SELECTOR, jobs)

    for job in job_list:
        # Loop through all the jobs in the list and clicking one by one    
        ActionChains(driver).move_to_element(job).double_click(job).perform()
        apply_to_job()  
        
        # checking if it last job
        if job_list.index(job) == len(job_list) - 1:
            break
        
    next_page() # if doesnt work then u have to break the for loop  

def apply_to_job():
    # elements
    global submitApplication, upload_resume, uncheckFollow, dismiss, nextButton1, choose, review
    
    alreadyApplied = '.display-flex .artdeco-inline-feedback__message' # Text element is inside this
    easyApply = '.display-flex .jobs-apply-button'
    nextButton1 = '[aria-label="Continue to next step"]'
    choose = 'button.artdeco-button--1' # Find all elements and choose 1st one
    review = '[aria-label="Review your application"]'
    uncheckFollow = '[id="follow-company-checkbox"]' # Check if this works first 
    submitApplication = '[aria-label="Submit application"]'
    dismiss = '.artdeco-modal__dismiss'
    upload_resume = '[aria-describedby="jobs-document-upload__resume-upload-subtitle"]' 
           
    # print(job_list.index(job))
    try: 
        # Checking if already applied
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, alreadyApplied)))        
    except:
        if "Apply" != WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.CSS_SELECTOR, easyApply))).text:
            try:
            # Application process
                easyApplyButton = WebDriverWait(driver,20).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, easyApply)))
                easyApplyButton.click();    
            except:
                pass
            
            try:
                driver.find_element(By.CSS_SELECTOR, submitApplication)
                short_application()
            except:
                long_application()        
            
            close_popup()
            write_to_excel()
           
def long_application():
    # Click first next button
    try:    
        driver.find_element(By.CSS_SELECTOR, nextButton1).click()
    except:
        pass
    
    # upload cv
    try:
        if job_list.index(job) == 0:
            driver.find_element(By.CSS_SELECTOR, upload_resume).click()
            time.sleep(1)
            p.write(resume_folder) 
            p.press('enter')  
            time.sleep(2) # Uploading CV takes time for website to process. click next button after delay otherwise it wont 
        else:
            driver.find_element(By.CSS_SELECTOR, choose).click()            
    except:
        pass
    
    # click second next button
    try: 
        driver.find_element(By.CSS_SELECTOR, nextButton1).click()
    except:
        pass
    
    # Review application
    try:
        time.sleep(5)
        driver.find_element(By.CSS_SELECTOR, review).click()
    except:
        pass
    
    # Uncheck follow button (doesnt work)
    try:
        uncheckFollowButton = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CSS_SELECTOR, uncheckFollow)))
        ActionChains(driver).scroll_to_element(uncheckFollowButton).move_to_element(uncheckFollowButton).click(uncheckFollowButton).perform()
    except:
        pass    
    
    # Submit application
    try:
        WebDriverWait(driver,300).until(EC.element_to_be_clickable((By.CSS_SELECTOR, submitApplication))).click()
    except:
        pass
    
    # Pop up that comes after application
    try:
        WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CSS_SELECTOR, dismiss))).click()
    except:
        pass


def short_application():
    # Upload CV
    try:
        driver.find_element(By.CSS_SELECTOR, upload_resume).click()
        time.sleep(1)
        p.write(resume_folder) 
        p.press('enter')                
    except:
        pass
    
    # Uncheck follow button (doesnt work)
    try:
        uncheckFollowButton = WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CSS_SELECTOR, uncheckFollow)))
        ActionChains(driver).scroll_to_element(uncheckFollowButton).move_to_element(uncheckFollowButton).click(uncheckFollowButton).perform()
    except:
        pass

    # Submit application
    try:
        WebDriverWait(driver,300).until(EC.element_to_be_clickable((By.CSS_SELECTOR, submitApplication))).click()
    except:
        pass
    
    # Pop up that comes after application
    try:
        WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CSS_SELECTOR, dismiss))).click()
    except:
        pass
    
    
  

def close_popup():
    try:
        WebDriverWait(driver,20).until(EC.presence_of_element_located((By.CSS_SELECTOR, dismiss))).click()
    except:
        pass
  
                
if __name__ == "__main__": 
    main()