from pandas import read_csv
import re

def main():
    cols = ['title', 'ingredients', 'instructions']
    recipes_df = read_csv("recipes.csv", names=cols, encoding='latin-1')

    preheat_oven_to = re.compile('\s*(\d|/|\\\|\s)+')
    temp_list = []
    for recipe in recipes_df['instructions']:
        # print(recipe)
        instructions = recipe.split(".")
        if 'reheat oven to ' in instructions[0]:
            idc, temp = instructions[0].split('reheat oven to ')
            temp_list.append(temp)
            instructions.pop(0)
        for instruction in instructions:
            # TODO could add tags


    print(temp_list)


if __name__ == '__main__':
    main()