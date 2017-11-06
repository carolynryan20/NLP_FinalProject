import requests
from recipe_scrapers import scrape_me as scrape
# https://github.com/hhursev/recipe-scraper


def crawl_allrecipes():
    init_req = requests.get('http://allrecipes.com/recipes/276/desserts/cakes')
    token = init_req.cookies['ARToken']
    headers = {'Authorization': 'Bearer ' + token}

    done = False
    page = 1
    urls = []
    while not done:
        root_url = 'https://apps.allrecipes.com/v1/assets/hub-feed?id=276&pageNumber={}&isSponsored=false&sortType=p'.format(page)
        r = requests.get(root_url, headers=headers)
        recipes = r.json()['cards']

        new = 0
        for recipe in recipes:
            if 'recipeUrl' in recipe:
                url = recipe['recipeUrl']
                if url not in urls:
                    urls.append('http://allrecipes.com{}'.format(url))
                    new += 1

        if new == 0:
            done = True

        print("Page {}: {} new recipes".format(page, new))
        page += 1


def crawl_epicurious():
    headers = {'x-requested-with': 'XMLHttpRequest'}

    done = False
    page = 1
    urls = []
    while not done:
        root_url = 'https://www.epicurious.com/search/?type=cake&page={}'.format(page)
        r = requests.get(root_url, headers=headers)
        items = r.json()['items']

        new = 0
        for item in items:
            if item['type'] == 'recipe':
                url = item['url']
                if url not in urls:
                    urls.append('https://www.epicurious.com{}'.format(url))
                    new += 1
                else:
                    print("DUPLICATE")

        if new == 0:
            done = True

        print("Page {}: {} new recipes".format(page, new))
        page += 1

    return urls


def scrape_recipes(recipe_urls):
    recipe_urls = open("allrecipes.txt", "r")
    recipe_csv = open("allrecipes.csv", "w")
    for url in recipe_urls.readlines():
        url = url.strip()
        while True:
            try:
                print('url:', url)
                scrape_recipe = scrape(url)

                r = scrape_recipe
                print(r.url)
                print(r.host())
                print(r.title())
                print(r.total_time())
                print(r.ingredients())
                print(r.instructions())

                title = scrape_recipe.title().replace(",", " ")
                ingredients = ";".join(scrape_recipe.ingredients()).replace(",", " ")
                # May want to split this out into more specified ingredients for easy data access
                instructions = scrape_recipe.instructions().replace(",", " ").replace("\n", "  ")
                recipe_csv.write("{}, {}, {}\n".format(title, ingredients, instructions))
                print(title)
                break
            except Exception as e:
                print('exception:', e)

    recipe_urls.close()
    recipe_csv.close()


def main():
    urls = crawl_allrecipes()
    urls.append(crawl_epicurious())

    with open('urls.txt', 'wb') as f:
        for url in urls:
            f.write(url)

    scrape_recipes(urls)


if __name__ == '__main__':
    main()
