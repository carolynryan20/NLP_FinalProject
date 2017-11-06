import nltk
from pandas import read_csv
import re

def main():
    cols = ['title', 'ingredients', 'instructions']
    recipes_df = read_csv("recipes.csv", names=cols, encoding='latin-1')
    # can get all columns with recipes_df.title, recipes_df.time, recipes_df.ingredients, recipes_df.instructions

    # print("Recipes DF",recipes_df)

    # print("Recipes DF Ingredients",recipes_df.ingredients[:1])
    bigList = createBigList(recipes_df)
    cleanBigList(bigList)

    for recipe in bigList:
        for ingredient in recipe:
            if 'package' in ' '.join(ingredient) and ingredient[1] != 'ounce' and ingredient[1] != 'g' and ingredient[1] != 'package':
                print(ingredient[0], "\t\t\t", ingredient[1], "\t\t\t", ingredient[2])

    # print("Big List", bigList)
    # print("Big List Recipe", bigList[8])
    # print("Big List Ingredient", bigList[8][0])
    # print("Big List Ingredient Quantity", bigList[8][0][0])
    # print("Big List Ingredient Measurement", bigList[8][0][1])
    # print("Big List Ingredient Type", bigList[8][0][2])

def createBigList(recipes_df):
    '''
    Creates a list of recipes where the we have [Recipe][IngredientList][
    :param recipes_df: dataframe of recipes
    :return: list of list of list
        biggest level is the ingredient list for every recipes
        second level is the ingredient list for a single recipe
        third and final level is ingredient, which is broken into quantity, amount and ingredient
    '''

    #This list will have raw list of ingredients
    listOfIngredients = []
    #This list will have list of lists where ingredients are seperated using regexs
    bigList = []

    #iterates through entire corpus of recipies
    for j in range(0,len(recipes_df.ingredients)):
        #seperated ingredients for each recipie
        recList = []
        #creates list of lists containing ingredient list
        listOfIngredients.append(list(recipes_df.ingredients.loc[j:j])[0].split(";"))

        #regex for qunatity
        numbers = re.compile('\s*(\d|/|\\\|\s)+')
        #regex for amount
        amounts = re.compile('\s*(\d|/|\\\|\s)+(\\(.*\\)|\w*)+')
        #regex for ingredient
        ingredients = re.compile('.*')

        #iterates through all ingredients for a single recipe
        for i in range(0,len(listOfIngredients[j])):
            #if match
            if numbers.match(listOfIngredients[j][i]):
                #used to append each element of an ingredient
                ingList = []
                #gets the quantity
                number = numbers.match(listOfIngredients[j][i])
                numberStr = number.group()
                #gets the amount
                amount = amounts.match(listOfIngredients[j][i])
                amountStr = amount.group()
                amountStr2 = amountStr.replace(number.group(),'')
                #gets the ingredient
                ingredient = ingredients.match(listOfIngredients[j][i])
                ingredientStr = ingredient.group()
                ingredientStr = ingredientStr.replace(amountStr,'')

                #misc fixes
                ingredientStr = ingredientStr[1:len(ingredientStr)]

                if amountStr2 == 'egg' or amountStr2 == 'eggs':
                    ingredientStr = 'egg ' + ingredientStr
                    amountStr2 = ''

                if amountStr2[:1] == '(':
                    amountStr2 = amountStr2[1:len(amountStr2)-1]

                if numberStr[:1] == ' ':
                    numberStr = numberStr[1:len(numberStr)]

                if amountStr2[len(amountStr2)-1:len(amountStr2)] == 's':
                    amountStr2 = amountStr2[0:len(amountStr2)-1]

                numberStr = numberStr[0:len(numberStr)-1]

                if ingredientStr[len(ingredientStr)-1:len(ingredientStr)] == ' ':
                    ingredientStr = ingredientStr[0:len(ingredientStr)-1]

                #appends quantity, amount, and ingredient to list
                ingList.append(numberStr)
                ingList.append(amountStr2)
                ingList.append(ingredientStr)

            #appends the list of the three factors to another list
            #this will have all the ingredients for a single recipe
            recList.append(ingList)
        #appends that list to a big list
        #this will have the recipe for every cake

        bigList.append(recList)
    # print(bigList[3])
    return bigList

def cleanBigList(bigList):
    for recipe_index in range(len(bigList)):
        recipe = bigList[recipe_index]
        for ingredient_index in range(len(recipe)):
            ingredient = recipe[ingredient_index]

            if 'package' in ingredient[2]:
                recipe_amt = get_float(ingredient[0])
                if recipe_amt:
                    if 'ounce' in ingredient[1] or "-oz" in ingredient[1]:
                        new_ingredient = []
                        ingredient[1] = ingredient[1].replace("-", " ") # Fixes 1 8-ounce package
                        ounce_amt = get_float(ingredient[1].split()[0])
                        if recipe_amt and ounce_amt:
                            # print("Ingredient", ingredient[0], "Ounce amt", ounce_amt)
                            new_ounce_amt = recipe_amt * ounce_amt
                            new_ingredient.append(str(new_ounce_amt)) # TODO if we make this float could be nice later
                            new_ingredient.append("ounce")
                            new_ingredient.append(ingredient[2])
                            bigList[recipe_index][ingredient_index] = new_ingredient
                        else:
                            # These ones are kinda weird, don't know why
                            pass
                            # print("NOT IN IF", ingredient)
                            # print("NOT IN IF Ingredient", ingredient[0], "Ounce amt", ounce_amt)
                    elif len(ingredient[1].split()) > 1 and 'g' == ingredient[1].split()[1]:
                        # print("Grams!", ingredient)
                        new_ingredient = []
                        gram_amt = get_float(ingredient[1].split()[0])
                        if recipe_amt and gram_amt:
                            # print("Ingredient", ingredient[0], "Ounce amt", ounce_amt)
                            new_gram_amt = recipe_amt * gram_amt
                            new_ingredient.append(str(new_gram_amt))  # TODO if we make this float could be nice later
                            new_ingredient.append("g")
                            new_ingredient.append(ingredient[2])
                            bigList[recipe_index][ingredient_index] = new_ingredient

def get_ingredient_list():
    user_input_ingredients = []
    ingredient = input("Enter an ingredient.  Hit 'q' when done entering ingredients. ")
    while ingredient != 'q' and ingredient:
        user_input_ingredients.append(ingredient)
        ingredient = input("Enter an ingredient.  Hit 'q' when done entering ingredients. ")

    print(user_input_ingredients)

    # Choose ingredient amounts
    # Select more ingredients if need be
    # Return complete ingredients

    get_ingredient_list()

def isfloat(value):
    # https://stackoverflow.com/questions/736043/checking-if-a-string-can-be-converted-to-float-in-python
    try:
        float(value)
        return True
    except ValueError:
        return False

def frac_to_float(frac_str):
    try:
        num, den = frac_str.split('/')
        if " " in num:
            wh, num = num.split()
        else:
            wh = 0
        result = float(wh) + float(num) / float(den)
        return result
    except ValueError:
        return None

def get_float(str):
    if isfloat(str):
        return float(str)
    frac = frac_to_float(str)
    if frac:
        return frac
    return None

if __name__ == '__main__':
    main()
