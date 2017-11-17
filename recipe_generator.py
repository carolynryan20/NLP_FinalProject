from pandas import read_csv
import re
from random import randint, choice
import numpy as np
from scipy.stats import norm
from nltk.tokenize import sent_tokenize

def main():
    cols = ['title', 'ingredients', 'instructions']
    recipes_df = read_csv("recipes.csv", names=cols, encoding='latin-1')
    # can get all columns with recipes_df.title, recipes_df.time, recipes_df.ingredients, recipes_df.instructions

    instruction_corpus = []
    for i in range(len(recipes_df.instructions)):
    	instruction_corpus.append(recipes_df.instructions.loc[i])

    # recipes_df.ingredients[:1]

    # Big List [Entire Recipe][Single Ingredient][0 = Amt, 1 = Unit, 2 = Food/Ingredient]
    bigList = createBigList(recipes_df)

    ingredient_list = set()
    for i in range(len(bigList)):
      for j in range(len(bigList[i])):
        ingredient_list.add(bigList[i][j][2])
    probDictAmt = createProbAmt(bigList)
    probDictUnits = createProbUnits(bigList)

    # Dict of form {ingredient: [unit of measurement, amt]}
    ingredient_dict = get_ingredient_dict(probDictAmt, probDictUnits)

    output_sents = []
    for k, v in ingredient_dict.items():
        ingredient_sents = []
        for recipe in instruction_corpus:
            recipe_sents = sent_tokenize(recipe)
            for sentence in recipe_sents:
                if k in str(sentence):
                    ingredient_sents.append(sentence)
        if ingredient_sents:
            output_sents.append(choice(ingredient_sents))
        else:
            print('Could not generate instructions for ingredient ' + k + '!')
		    
    print(output_sents)		    
		


    # print(calcPval(probDict, "egg", 10))
    # print(returnQuant(probDict, "egg"))

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
    return bigList

def createProbAmt(bigList):
    probDict = {}
    for i in range(0,len(bigList)):
        for j in range(0,len(bigList[i])):
            if bigList[i][j][2] not in probDict:
                quantityList = []
                quantityList.append(bigList[i][j][0])
                probDict[bigList[i][j][2]] = quantityList
            else:
                probDict[bigList[i][j][2]].append(bigList[i][j][0])
    return probDict

def createProbUnits(bigList):
    probDict = {}
    for i in range(0, len(bigList)):
        for j in range(0, len(bigList[i])):
            units = bigList[i][j][1]
            if bigList[i][j][2] not in probDict:
                quantityList = []
                quantityList.append(units)
                probDict[bigList[i][j][2]] = quantityList
            else:
                probDict[bigList[i][j][2]].append(units)
    return probDict

def returnQuant(probDict, food):
    index = randint(0,len(probDict[food])-1)
    return (get_float(probDict[food][index]))

def returnUnit(probDict, food):
    index = randint(0, len(probDict[food]) - 1)
    return (probDict[food][index])

def calcPval(probDict,food,quant):
    sampleList = []
    for i in range(0,1000):
        sampleList.append(int(returnQuant(probDict,food)))
    sampMean = np.mean(sampleList)
    sampSD = np.std(sampleList)
    zscore = (quant - sampMean)/sampSD
    if zscore < 0:
        pval = norm.cdf(zscore) + (1-norm.cdf(-zscore))
    else:
        pval = (1 - norm.cdf(zscore)) + norm.cdf(-zscore)

    return pval

def cleanBigList(bigList):
    '''
    When recipe calls for 2 (8 ounce) packages <INGREDIENT>, we want 16 ounce <INGREDIENT>
    :param bigList: Ingredient big list
    :return: Big list with above change
    '''
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

def get_ingredient_dict(probDictAmt, probDictUnits):
    '''
    Function that allows user to input ingredients
    :param probDictAmt: {ingredient: [list of possible amounts]}
    :param probDictUnits: {ingredient: [list of possible units used for that ingredient]}
    :return: ingredient_dict: {ingredient: [units, amt]}
    '''
    ingredient_dict = {}
    ingredient = input("Enter an ingredient.  Hit 'q' when done entering ingredients. ")
    while ingredient != 'q' and ingredient:
        if ingredient in probDictAmt and ingredient not in ingredient_dict:
            amt = returnQuant(probDictAmt, ingredient)
            units = returnUnit(probDictUnits, ingredient)
            print("Use {} {} {} in recipe".format(amt, units, ingredient)) # NEED UNITS
            ingredient_dict[ingredient] = [units, amt]
        elif ingredient in ingredient_dict:
            print("You have already used this in your cake!")
        else:
            print("You can't put that in a cake!")
        ingredient = input("Enter an ingredient.  Hit 'q' when done entering ingredients. ")

    extra = int(input("How many more ingredients would you like in your cake? "))
    count = 0
    while count < extra:
        ingredient = choice(list(probDictAmt.keys()))
        amt = returnQuant(probDictAmt, ingredient)
        units = returnUnit(probDictUnits, ingredient)
        if ingredient not in ingredient_dict:
            ingredient_dict[ingredient] = [units, amt]
            count += 1

    print(ingredient_dict)
    return ingredient_dict

def isfloat(value):
    '''
    Returns whether or not a value can be cast to a float
    https://stackoverflow.com/questions/736043/checking-if-a-string-can-be-converted-to-float-in-python
    :param value: str
    :return: boolean, True = can be a float
    '''
    try:
        float(value)
        return True
    except ValueError:
        return False

def frac_to_float(frac_str):
    '''
    Given a string, returns the a float if string is fraction
    :param frac_str: str
    :return: float if possible, none otherwise
    '''
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
    '''
    Given a string, converts it to a float
    :param str: can be int, decimal, or fraction (in a string)
    :return: float if conversion possible, None else
    '''
    if isfloat(str):
        return float(str)
    frac = frac_to_float(str)
    if frac:
        return frac
    return None

if __name__ == '__main__':
    main()
