import nltk
from pandas import read_csv
def main():
    cols = ['title', 'time', 'ingredients', 'instructions']
    recipes_df = read_csv("cake_recipe.csv", names=cols)
    # can get all columns with recipes_df.title, recipes_df.time, recipes_df.ingredients, recipes_df.instructions

    print(recipes_df)

def get_ingredient_list():
    user_input_ingredients = []
    ingredient = input("Enter an ingredient.  Hit q when done entering ingredients. ")
    while ingredient != 'q' and ingredient:
        user_input_ingredients.append(ingredient)
        ingredient = input("Enter an ingredient.  Hit q when done entering ingredients. ")

    print(user_input_ingredients)

    # Choose ingredient amounts
    # Select more ingredients if need be
    # Return complete ingredients

if __name__ == '__main__':
    # main()
    get_ingredient_list()