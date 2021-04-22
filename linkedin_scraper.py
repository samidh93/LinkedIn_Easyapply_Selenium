from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, ElementClickInterceptedException, NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select

import time
import re
import json
import requests
import urllib
from bs4 import BeautifulSoup
import urllib.request

with open('config.json') as config_file:
    data = json.load(config_file)

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
email = data['email']
password = data['password']
keywords = data['keywords']
location = data['location']
driver = webdriver.Chrome(options=options, executable_path=data['driver_path'])

def login():
    # go to the LinkedIn login url
    driver.get("https://www.linkedin.com/login")
    # introduce email and password and hit enter
    login_email = driver.find_element_by_name('session_key')
    login_email.clear()
    login_email.send_keys(email)
    login_pass = driver.find_element_by_name('session_password')
    login_pass.clear()
    login_pass.send_keys(password)
    login_pass.send_keys(Keys.RETURN)
    time.sleep(1)
    speicher = driver.find_element_by_xpath('//*[@id="remember-me-prompt__form-primary"]/button')
    speicher.click()
    time.sleep(5)

def search_filter(i, j):
    jobs_link = driver.find_element_by_link_text('Jobs')
    jobs_link.click()
    time.sleep(5)
    # search based on keywords and location and hit enter
    search_keywords = driver.find_element_by_xpath('//*[@class="jobs-search-box__text-input jobs-search-box__keyboard-text-input"]')
    #search_keywords.clear()
    search_keywords.send_keys(keywords[i])
    search_location = driver.find_element_by_xpath('//*[@class="jobs-search-box__text-input"]')
    #search_location.clear()
    search_location.send_keys(location[j])
    search_location.send_keys(Keys.RETURN)
    time.sleep(2)
    easy_apply_button = driver.find_element_by_xpath("//button[@aria-label='Easy Apply filter.']")
    easy_apply_button.click()

def count_results():
    total_results = driver.find_element_by_class_name("display-flex.t-12.t-black--light.t-normal")
    total_results_int = int(total_results.text.split(' ',1)[0].replace(",",""))
    print(total_results_int)


def submit_apply(job_add):
    """This function submits the application for the job add found"""
    print('You are applying to the position of: ', job_add.text)
    job_add.click()
    # click on the easy apply button, skip if already applied to the position
    try:
        in_apply = driver.find_element_by_xpath("//button[@data-control-name='jobdetails_topcard_inapply']")
        in_apply.click()
    except NoSuchElementException:
        print('You already applied to this job, go to next...')
        applied = True
        pass
    driver.implicitly_wait(3)
    # try to submit if submit application is available...
    try:
        try:
            # if next is shown
            continue_job = driver.find_element_by_xpath("//button[@aria-label='Continue to next step']")
            continue_job.click()
            driver.implicitly_wait(3)
        except:
            print('no next..')
            pass
        try:
            # if another next is shown
            continue_job = driver.find_element_by_xpath("//button[@aria-label='Continue to next step']")
            continue_job.click()
            driver.implicitly_wait(3)
        except:
            print('no 2 next..')
            pass
        try:
            # if options to select given
            select = Select(driver.find_element_by_id('urn:li:fs_easyApplyFormElement:(urn:li:fs_normalized_jobPosting:2462810884,21613107,multipleChoice)'))
            # select by visible text
            select.select_by_visible_text('Verhandlungssicher')
            driver.implicitly_wait(3)
        except:
            print('no options..')
            pass
        try:
            # if input field are demanded
            input_field = driver.find_elements_by_class_name("ember-text-field.ember-view.fb-single-line-text__input")
            for f in input_field:
                f.clear()
                f.send_keys('2')
            driver.implicitly_wait(3)
        except:
            print('no inputs..')
            pass
        try:
            # if review job demand
            continue_job = driver.find_element_by_xpath("//button[@aria-label='Review your application']")
            continue_job.click()
            driver.implicitly_wait(3)
        except:
            print('not reviewing..')
            pass
        finally:
            # finally submit application
            submit = driver.find_element_by_xpath("//button[@data-control-name='submit_unify']")
            submit.send_keys(Keys.RETURN)
            driver.implicitly_wait(3)
            try:
                # after submit close window
                closing = driver.find_element_by_xpath("//button[@aria-label='Dismiss']")
                closing.click()
                driver.implicitly_wait(3)
            except:
                print('no close popup')
                pass  
    # ... if not available, discard application and go to next
    except NoSuchElementException:
        applied = True
        print('Not direct application, going to next...')
        try:
            discard = driver.find_element_by_xpath("//button[@data-test-modal-close-btn]")
            discard.send_keys(Keys.RETURN)
            driver.implicitly_wait(3)
            discard_confirm = driver.find_element_by_xpath("//button[@data-test-dialog-primary-btn]")
            discard_confirm.send_keys(Keys.RETURN)
            driver.implicitly_wait(3)
        except NoSuchElementException:
            pass
            return applied


if __name__ == '__main__':

    for j in range(len(location)):
        for i in range(len(keywords)):
            login()
            search_filter(i, j)
            count_results()
            url = driver.current_url
            results = driver.find_elements_by_class_name("jobs-search-results__list-item.occludable-update.p0.relative.ember-view")
            for result in results:
                try:
                    hover = ActionChains(driver).move_to_element(result)
                    hover.perform()
                    titles = result.find_elements_by_class_name('full-width.artdeco-entity-lockup__title.ember-view')
                    driver.implicitly_wait(3)
                    for title in titles:
                        try:
                            submit_apply(title)
                            driver.implicitly_wait(3)
                        except:
                            print('skipping')
                            continue
                except:
                    print('no results')
                    pass
