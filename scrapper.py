from recipe_scrapers import scrap_me as scrape
# https://github.com/hhursev/recipe-scraper

def main():
    recipe_urls = open("cake_recipe_urls.txt", "r")
    recipe_csv = open("cake_recipe.csv", "w")
    for url in recipe_urls.readlines():
        scrape_recipe = scrape(url)
        title = scrape_recipe.title().replace(",", " ")
        ingredients = ";".join(scrape_recipe.ingredients()).replace(",", " ")
        # May want to split this out into more specified ingredients for easy data access
        instructions = scrape_recipe.instructions().replace(",", " ").replace("\n", "  ")

        # Might not be (and by might I mean definitely isn't) the best way to keep this data
        recipe_csv.write("{}, {}, {}, {}\n".format(
            title, scrape_recipe.total_time(), ingredients, instructions))

        print("Title: {}, Time: {}\nIngredients: {}\nInstructions: {}\n".format(
            scrape_recipe.title(), scrape_recipe.total_time(), scrape_recipe.ingredients(), scrape_recipe.instructions()))

    recipe_urls.close()
    recipe_csv.close()

if __name__ == '__main__':
    main()