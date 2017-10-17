import nltk
from pandas import read_csv
def main():
    cols = ['title', 'time', 'ingredients', 'instructions']
    recipes_df = read_csv("cake_recipe.csv", names=cols)
    # can get all columns with recipes_df.title, recipes_df.time, recipes_df.ingredients, recipes_df.instructions

    print(recipes_df)
    
if __name__ == '__main__':
    main()