import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Scrape FIFA rankings from the website
def scrape_fifa_rankings():
    url = "https://football-ranking.com/fifa-rankings"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    rankings = []

    # Parse the rankings table
    table = soup.find('table', class_='ml-1 table table-striped table-bordered table-hover')
    tbody = table.find('tbody')

    for row in tbody.find_all('tr')[:50]:
        columns = row.find_all('td')
        if len(columns) > 2:
            team = (columns[1].text.strip())[:-6]
            flag = columns[1].find('img')['src']
            rankings.append({'team': team, 'flag': flag})

    return rankings

# Scrape Quini6 draw numbers and draw date
def scrape_quini_numbers():
    url = "https://www.quini-6-resultados.com.ar"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')
    quini_numbers = []

    # Parse the draw numbers
    sets = soup.find_all('td', class_='nro')
    for num_set in sets:
        quini_numbers.append(num_set.text.strip())

    # Process the draw numbers
    processed_quini_numbers = [
        [int(num.strip()) for num in draw.split(' - ')]
        for draw in quini_numbers
    ]

    # Extract and format the draw date
    tdate = soup.find('p', class_='lead').find('strong').text.strip()
    match = re.search(r'\d{2}/\d{2}/\d{4}', tdate)
    if match:
        date_str = match.group(0)
        formatted_date = datetime.strptime(date_str, '%d/%m/%Y').date()
    else:
        raise ValueError('Date not found')

    return processed_quini_numbers, formatted_date

if __name__ == "__main__":
    # Test the scraping functions
    fifa_rankings = scrape_fifa_rankings()
    for ranking in fifa_rankings:
        print(ranking)
    quini_numbers, draw_date = scrape_quini_numbers()
    print(f'Draw Date: {draw_date}')
    for num_set in quini_numbers:
        print(num_set)