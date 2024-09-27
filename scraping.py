import requests
from bs4 import BeautifulSoup

def scrape_fifa_rankings():
    url = "https://football-ranking.com/fifa-rankings"

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    rankings = []
    table = soup.find('table', class_ = 'ml-1 table table-striped table-bordered table-hover')
    tbody = table.find('tbody')

    for row in tbody.find_all('tr')[:50]:
        columns = row.find_all('td')
        if len(columns) > 2:
            team = (columns[1].text.strip())[:-6]
            flag = columns[1].find('img')['src']

            rankings.append({
                'team' : team,
                'flag' : flag
            })

    return rankings

def scrape_quini_numbers():
    url = "https://www.quini-6-resultados.com.ar"

    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, 'html.parser')

    quini_numbers = []
    sets = soup.find_all('td', class_ = 'nro')

    for num_set in sets:
        quini_numbers.append(num_set.text.strip())

    processed_quini_numbers = []

    for draw in quini_numbers:
        numbers = [int(num.strip()) for num in draw.split(' - ')]
        processed_quini_numbers.append(numbers)

    return processed_quini_numbers

if __name__ == "__main__":
    fifa_rankings = scrape_fifa_rankings()
    for ranking in fifa_rankings:
        print(ranking)
    quini_numbers = scrape_quini_numbers()
    for num_set in quini_numbers:
        print(num_set)