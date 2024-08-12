import requests
from bs4 import BeautifulSoup
import csv
import time

def get_list_items(url):
    print(f"fetching film urls...")
    items = []
    
    while url:
        response = requests.get(url)
        
        # check if req was successful
        if response.status_code != 200:
            print(f"Failed to retrieve the webpage. Status code: {response.status_code}")
            break
        
        # parse contents
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # find every film item
        list_items = soup.find_all('div', class_='poster')
        
        # save their url for later
        for item in list_items:
            if 'data-target-link' in item.attrs:
                film_url = 'https://letterboxd.com' + item['data-target-link']
                items.append(film_url)
        
        # take pagination into account to grab whole list
        next_button = soup.find('a', class_='next')
        url = 'https://letterboxd.com' + next_button['href'] if next_button else None
    
    return items

def get_film_details(film_url):
    print(f"grabbing info from {film_url}")

    response = requests.get(film_url)
    
    # check if req was successful
    if response.status_code != 200:
        print(f"Failed to retrieve the film page. Status code: {response.status_code}")
        return None
    
    # parse content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # extract film details
    title = soup.find('span', class_='name js-widont prettify').text.strip() if soup.find('h1', class_='filmtitle') else 'No title'
    description = soup.find('div', class_='truncate').text.strip() if soup.find('div', class_='truncate') else 'No description'
    release_year = soup.find('div', class_='releaseyear').text.strip() if soup.find('div', class_='releaseyear') else 'No release year'
    genre = soup.find('div', class_='text-sluglist capitalize').contents[1].find('a').text.strip() if soup.find('div', class_='text-sluglist capitalize').contents[1] else 'No genre'
    director = soup.find('a', class_='contributor').contents[0].text.strip() if soup.find('a', class_='contributor').contents[0] else 'No director'
    
    return [title, description, release_year, genre, director, film_url]

# hardcoded lb list - later make this an input
url = "https://letterboxd.com/dave/list/official-top-250-narrative-feature-films/"

# find all top 250 films
film_urls = get_list_items(url)

# create csv to store data
csv_file = 'films.csv'
with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Title', 'Description', 'Release Year', 'Genre', 'Director', 'URL'])

    # for each film, get relevant info
    for film_url in film_urls:
        film_details = get_film_details(film_url)
        if film_details:
            writer.writerow(film_details)
        
        # chill
        time.sleep(1)

print(f"Data has been written to {csv_file}")
