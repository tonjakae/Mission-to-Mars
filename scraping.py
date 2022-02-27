# Import Splinter, BeautifulSoup, and Pandas
from splinter import Browser
import bs4
from bs4 import BeautifulSoup as soup
from webdriver_manager.firefox import GeckoDriverManager
import pandas as pd
import datetime as dt

# Setup splinter
# executable_path = {'executable_path': GeckoDriverManager().install()} "/Users/sebastian/myPrograming_Coding/Selenium_Drivers/geckodriver"

#browser = Browser('firefox', executable_path="/usr/local/bin/geckodriver", headless=False)

def scrape_all():
    # Initiate headless driver for deployment
    browser = Browser('firefox', executable_path="/usr/local/bin/geckodriver", headless=True)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in a dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(),
        "png_urls_titles":scrape_urls_and_titles(browser), 
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data


def mars_news(browser):

    # Scrape Mars News
    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Convert the browser html to a soup object and then quit the browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one("ul.item_list li.slide")
        # Use the parent element to find the first 'a' tag and save it as 'news_title'
        news_title = slide_elem.find("div", class_="content_title").get_text()
        # Use the parent element to find the paragraph text
        news_p = slide_elem.find("div", class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None

    return news_title, news_p


def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')[0]
    full_image_elem.click()

    # Find the more info button and click that
    browser.is_element_present_by_text('more info', wait_time=1)
    more_info_elem = browser.links.find_by_partial_text('more info')
    more_info_elem.click()

    # Parse the resulting html with soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    # Add try/except for error handling
    try:
        # Find the relative image url
        img_url_rel = img_soup.select_one('figure.lede a img').get("src")

    except AttributeError:
        return None

    # Use the base url to create an absolute url
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

def mars_facts():
    # Add try/except for error handling
    try:
        # Use 'read_html' to scrape the facts table into a dataframe
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['Description', 'Mars']
    df.set_index('Description', inplace=True)

    # Convert dataframe into HTML format, add bootstrap
    return df.to_html(classes="table table-striped")

def scrape_urls_and_titles(browser):
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)

    base_url = 'https://astrogeology.usgs.gov/'

    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []

    # 3. Write code to retrieve the image urls and titles for each hemisphere.

    #create soup object
    webpage_soup = soup(browser.html,"html.parser")

    #create list object conataining all relative 'divs'
    divs_list = webpage_soup.find_all('div', class_='item')

    #iterate through divs_list object to collect relevent info ie titles, descriptions, and img links
    titles = [i.find('h3').get_text() for i in divs_list]
    #descriptions = [i.find('p').get_text() for i in divs_list]

    # use a for loops to navigate to each item in the divs_list and scrape the img url by title name using browser.find_by_text()
    for i in titles:
        browser.find_by_text(i).click()
        hot_cauldren = soup(browser.html,"html.parser")
        hemisphere_image_urls.append({'img_url':f"{base_url}{hot_cauldren.find('img', class_='wide-image').get('src')}",'title':i})
        browser.visit(url)
    
    #df = pd.DataFrame(hemisphere_image_urls)
    #return df.to_html(classes="table table-striped")
    
    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())