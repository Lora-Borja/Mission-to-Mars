# Import tools
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
   
    # Initiate headless driver for deployment
    # Set the executable path and initialize the chrome browser in splinter (For Windows user)
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=False)

    news_title, news_paragraph = mars_news(browser)

    # Run all scraping functions and store results in dictionary
    data = {
        "news_title": news_title,
        "news_paragraph": news_paragraph,
        "featured_image": featured_image(browser),
        "facts": mars_facts(browser),
        "hemispheres": mars_hemispheres(browser),
        "last_modified": dt.datetime.now()
    }

    # Stop webdriver and return data
    browser.quit()
    return data

# Scrape Mars News
def mars_news(browser):

    # Visit the mars nasa news site
    url = 'https://mars.nasa.gov/news/'
    browser.visit(url)

    # Optional delay for loading the page
    browser.is_element_present_by_css("ul.item_list li.slide", wait_time=1)

    # Set up the HTML parser
    html = browser.html
    news_soup = soup(html, 'html.parser')
    
    # Add try/except for error handling
    try:
        slide_elem = news_soup.select_one('ul.item_list li.slide')

        # Assign the title and summary text to variables to reference later
        #slide_elem.find("div", class_='content_title')

        # Use the parent element to find the first 'a' tag and save it as news_title
        news_title = slide_elem.find("div", class_='content_title').get_text()

        # Use the parent element to find the paragraph text
        news_p = slide_elem.find('div', class_="article_teaser_body").get_text()

    except AttributeError:
        return None, None  

    return news_title, news_p

### Featured Mars Image
def featured_image(browser):
    # Visit URL
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)

    # Find and click the full image button
    full_image_elem = browser.find_by_id('full_image')
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

    # Use the base URL to create an absolute URL
    img_url = f'https://www.jpl.nasa.gov{img_url_rel}'

    return img_url

### Mars Facts
def mars_facts(browser):

    # Add try/except for error handling
    try:
        # Create a pandas DataFrame to house the table of facts
        df = pd.read_html('http://space-facts.com/mars/')[0]

    except BaseException:
        return None

    # Assign columns and set index of dataframe
    df.columns=['description', 'value']
    df.set_index('description', inplace=True)

    # Convert the DF back into HTML for the web app
    return df.to_html(classes="table table-striped")

    ### Mars Hemispheres
def mars_hemispheres(browser):
    
    # 1. Use browser to visit the URL 
    url = 'https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(url)
    
    # Assign the main_url
    main_url = 'https://astrogeology.usgs.gov/'
    html = browser.html
    img_soup = soup(html, 'html.parser')
    
    # 2. Create a list to hold the images and titles.
    hemisphere_image_urls = []
    
    # 3. Write code to retrieve the image urls and titles for each hemisphere.

    # Results returned as an iterable list
    results = img_soup.find_all('div', class_='item')

    # Loop through returned results
    for result in results:
        
        # Retrieve the titles
        title = result.find('h3').text
        
        # Get the link to go the full image site
        img_url = result.find('a')['href']
        
        # Creating the full_img_url
        full_img_url = main_url + img_url
        
        # Use browser to go to the full image url and set up the HTML parser
        browser.visit(full_img_url)
        html = browser.html
        img_soup = soup(html, 'html.parser')
        
        # Retrieve the full image urls
        hemisphere_img = img_soup.find('div',class_='downloads')
        hemisphere_full_img = hemisphere_img.find('a')['href']
        
        # Printing hemisphere_full_img
        print(hemisphere_full_img)
        
        # Creating hemispheres dict
        hemispheres = dict({'img_url':hemisphere_full_img, 'title':title})
    
        #Append the hemisphere_image_urls list
        hemisphere_image_urls.append(hemispheres)

    # 4. Return the list that holds the dictionary of each image url and title.
    return hemisphere_image_urls

if __name__ == "__main__":

    # If running as script, print scraped data
    print(scrape_all())
