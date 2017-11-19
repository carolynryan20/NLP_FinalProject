from pandas import read_csv
import re
from random import randint, choice
import numpy as np
from scipy.stats import norm
from nltk.tokenize import sent_tokenize
from string import punctuation

class RecipeGenerator:
    def __init__(self):
        cols = ['title', 'ingredients', 'instructions']
        self.recipes_df = read_csv("recipes.csv", names=cols, encoding='latin-1')
        # can get all columns with recipes_df.title, recipes_df.time, recipes_df.ingredients, recipes_df.instructions

        self.createKnownFoodList()
        self.createBigList()
        self.createProbDictAmt()
        self.createProbDictUnits()

    def createProbDictAmt(self):
        probDict = {}
        for i in range(0, len(self.bigList)):
            for j in range(0, len(self.bigList[i])):
                if len(self.bigList[i][j]) < 3:
                    # print(self.bigList[i][j])
                    continue
                if self.bigList[i][j][2] not in probDict:
                    quantityList = []
                    quantityList.append(self.bigList[i][j][0])
                    probDict[self.bigList[i][j][2]] = quantityList
                else:
                    probDict[self.bigList[i][j][2]].append(self.bigList[i][j][0])
        self.probDictAmt = probDict

    def createProbDictUnits(self):
        probDict = {}
        for i in range(0, len(self.bigList)):
            for j in range(0, len(self.bigList[i])):
                units = self.bigList[i][j][1]
                if self.bigList[i][j][2] not in probDict:
                    quantityList = []
                    quantityList.append(units)
                    probDict[self.bigList[i][j][2]] = quantityList
                else:
                    probDict[self.bigList[i][j][2]].append(units)
        self.probDictUnits = probDict

    def createBigList(self):
        '''
        Creates a list of recipes where the we have [Recipe][IngredientList][
        :param recipes_df: dataframe of recipes
        :return: list of list of list
            biggest level is the ingredient list for every recipes
            second level is the ingredient list for a single recipe
            third and final level is ingredient, which is broken into quantity, amount and ingredient
        '''
        # This list will have raw list of ingredients
        listOfIngredients = []
        # This list will have list of lists where ingredients are seperated using regexs
        bigList = []

        # iterates through entire corpus of recipies
        for j in range(0, len(self.recipes_df.ingredients)):
            # seperated ingredients for each recipie
            recList = []
            # creates list of lists containing ingredient list
            listOfIngredients.append(list(self.recipes_df.ingredients.loc[j:j])[0].split(";"))

            # regex for qunatity
            numbers = re.compile('\s*(\d|/|\\\|\s)+')
            # regex for amount
            amounts = re.compile('\s*(\d|/|\\\|\s)+(\\(.*\\)|\w*)+')
            # regex for ingredient
            ingredients = re.compile('.*')

            # iterates through all ingredients for a single recipe
            for i in range(0, len(listOfIngredients[j])):
                # if match
                ingList = []
                if numbers.match(listOfIngredients[j][i]):
                    # used to append each element of an ingredient
                    ingList = []
                    # gets the quantity
                    number = numbers.match(listOfIngredients[j][i])
                    numberStr = number.group()
                    # gets the amount
                    amount = amounts.match(listOfIngredients[j][i])
                    amountStr = amount.group()
                    amountStr2 = amountStr.replace(number.group(), '')
                    # gets the ingredient
                    ingredient = ingredients.match(listOfIngredients[j][i])
                    ingredientStr = ingredient.group()
                    ingredientStr = ingredientStr.replace(amountStr, '')

                    # misc fixes
                    ingredientStr = ingredientStr[1:len(ingredientStr)]

                    if amountStr2 == 'egg' or amountStr2 == 'eggs':
                        ingredientStr = 'egg ' + ingredientStr
                        amountStr2 = ''

                    if amountStr2[:1] == '(':
                        amountStr2 = amountStr2[1:len(amountStr2) - 1]

                    if numberStr[:1] == ' ':
                        numberStr = numberStr[1:len(numberStr)]

                    if amountStr2[len(amountStr2) - 1:len(amountStr2)] == 's':
                        amountStr2 = amountStr2[0:len(amountStr2) - 1]

                    if len(amountStr2.split()) > 1 and not "/" in amountStr2.split()[1]:
                        amountStr2 = amountStr2.split()[0]

                    numberStr = numberStr[0:len(numberStr) - 1]

                    if ingredientStr[len(ingredientStr) - 1:len(ingredientStr)] == ' ':
                        ingredientStr = ingredientStr[0:len(ingredientStr) - 1]

                    ingredientStr = self.find_valid_foods(ingredientStr)
                    if not ingredientStr:
                        continue

                    # appends quantity, amount, and ingredient to list
                    ingList.append(numberStr)
                    ingList.append(amountStr2)
                    ingList.append(ingredientStr)

                # appends the list of the three factors to another list
                # this will have all the ingredients for a single recipe
                if ingList:
                    recList.append(ingList)
            # appends that list to a big list
            # this will have the recipe for every cake
            if recList:
                bigList.append(recList)

        # Good way to see ingredients TODO delete
        ing_list = []
        for rec in bigList:
            for ing in rec:
                if (len(ing) > 2) and ing[2] not in ing_list:
                    ing_list.append(ing[2])
        ing_list.sort()

        with open("biglist.txt", 'w') as f:
            for ing in ing_list:
                f.write(ing)
                f.write("\n")

        self.bigList = bigList

    # TODO do we still need this?? We aren't really using amounts for any sort of ratio calculation as we thought we might
    def cleanBigList(self):
        '''
        When recipe calls for 2 (8 ounce) packages <INGREDIENT>, we want 16 ounce <INGREDIENT>
        :param bigList: Ingredient big list
        :return: Big list with above change
        '''
        for recipe_index in range(len(self.bigList)):
            recipe = self.bigList[recipe_index]
            for ingredient_index in range(len(recipe)):
                ingredient = recipe[ingredient_index]

                if 'package' in ingredient[2]:
                    recipe_amt = self.get_float(ingredient[0])
                    if recipe_amt:
                        if 'ounce' in ingredient[1] or "-oz" in ingredient[1]:
                            new_ingredient = []
                            ingredient[1] = ingredient[1].replace("-", " ")  # Fixes 1 8-ounce package
                            ounce_amt = self.get_float(ingredient[1].split()[0])
                            if recipe_amt and ounce_amt:
                                new_ounce_amt = recipe_amt * ounce_amt
                                new_ingredient.append(
                                    str(new_ounce_amt))  # TODO if we make this float could be nice later
                                new_ingredient.append("ounce")
                                new_ingredient.append(ingredient[2])
                                self.bigList[recipe_index][ingredient_index] = new_ingredient
                            else:
                                # These ones are kinda weird, don't know why
                                pass
                        elif len(ingredient[1].split()) > 1 and 'g' == ingredient[1].split()[1]:
                            new_ingredient = []
                            gram_amt = self.get_float(ingredient[1].split()[0])
                            if recipe_amt and gram_amt:
                                new_gram_amt = recipe_amt * gram_amt
                                new_ingredient.append(
                                    str(new_gram_amt))  # TODO if we make this float could be nice later
                                new_ingredient.append("g")
                                new_ingredient.append(ingredient[2])
                                self.bigList[recipe_index][ingredient_index] = new_ingredient

    def returnQuant(self, food):
        index = randint(0, len(self.probDictAmt[food]) - 1)
        return (self.get_float(self.probDictAmt[food][index]))

    def returnUnit(self, food):
        index = randint(0, len(self.probDictUnits[food]) - 1)
        return (self.probDictUnits[food][index])

    def calcPval(self, food, quant):
        sampleList = []
        for i in range(0, 1000):
            sampleList.append(int(self.returnQuant(food)))
        sampMean = np.mean(sampleList)
        sampSD = np.std(sampleList)
        zscore = (quant - sampMean) / sampSD
        if zscore < 0:
            pval = norm.cdf(zscore) + (1 - norm.cdf(-zscore))
        else:
            pval = (1 - norm.cdf(zscore)) + norm.cdf(-zscore)

        return pval


    def createKnownFoodList(self):
        '''
        Returns list of known foods
        :return:
        '''
        with open("new_food_list.txt", 'r') as f:
            _known_food_list = f.readlines()

        known_food_list = []
        for food in _known_food_list:
            if food[-1] == '\n':
                food = food[:-1]
            known_food_list.append(food.lower())
        self.known_food_list = known_food_list

    def find_valid_foods(self, ingredientStr):
        '''
        Edits some of the ingredients into more recognizable ingredients
        :param ingredientStr:
        :param known_food_list:
        :return:
        '''
        if ingredientStr == '':
            return None
        ingredientStr = ingredientStr.lower()
        ingredientStr = ''.join(ch for ch in ingredientStr if ch not in punctuation)
        if ingredientStr in self.known_food_list:
            return ingredientStr

        ingredientStr1 = ''
        for food in self.known_food_list:
            if food in ingredientStr.split() or food + "s" in ingredientStr.split():  # covers some plurality
                ingredientStr1 += food + " "

        if ingredientStr1 == '' and ingredientStr != '':
            return None

        # Reorders so juice orange should become orange juice, vanilla extract, cream cheese
        ingredientStr2 = ''
        for word in ingredientStr.split():
            if word in ingredientStr1 and word not in ingredientStr2:
                ingredientStr2 += word + " "

        if ingredientStr2 != '':
            if ingredientStr2[-1] == " ":
                ingredientStr2 = ingredientStr2[:-1]
            return ingredientStr2
        else:
            return None

    def get_ingredients_from_user(self):
        '''
        Function that allows user to input ingredients
        :param probDictAmt: {ingredient: [list of possible amounts]}
        :param probDictUnits: {ingredient: [list of possible units used for that ingredient]}
        :return: ingredient_dict: {ingredient: [units, amt]}
        '''
        ingredient_dict = {}
        ingredient = input("Enter an ingredient.  Hit 'q' when done entering ingredients. ")
        while ingredient != 'q' and ingredient:
            if ingredient in self.probDictAmt and ingredient not in ingredient_dict:
                amt = self.returnQuant(ingredient)
                units = self.returnUnit(ingredient)
                print("Use {} {} {} in recipe".format(amt, units, ingredient))  # NEED UNITS
                ingredient_dict[ingredient] = [units, amt]
            elif ingredient in ingredient_dict:
                print("You have already used this in your cake!")
            else:
                print("You can't put that in a cake!")
            ingredient = input("Enter an ingredient.  Hit 'q' when done entering ingredients. ")

        extra = int(input("How many more ingredients would you like in your cake? "))
        count = 0
        while count < extra:
            ingredient = choice(list(self.probDictAmt.keys()))
            amt = self.returnQuant(ingredient)
            units = self.returnUnit(ingredient)
            # print(ingredient, amt, units)
            if ingredient not in ingredient_dict:
                ingredient_dict[ingredient] = [units, amt]
                count += 1

        # print(ingredient_dict)
        return ingredient_dict

    def generate_output_sentences(self, ingredient_dict, match_ingredients_to_instructions):
        instruction_corpus = []
        for i in range(len(self.recipes_df.instructions)):
            instruction_corpus.append(self.recipes_df.instructions.loc[i])

        output_sents = []
        preheat_sents = []
        for recipe in instruction_corpus:
            recipe_sents = sent_tokenize(recipe)
            for sentence in recipe_sents:
                sentence = sentence.split(' ')
                if ('preheat' in str(sentence[0])) or ('Preheat' in str(sentence[0])):
                    preheat_sents.append((' ').join(sentence))
        output_sents.append(choice(preheat_sents))

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

        if match_ingredients_to_instructions:
            ingredient_dict = self.extract_ingredients(output_sents, ingredient_dict)
        return output_sents, ingredient_dict

    def extract_ingredients(self, output_sents, ingredient_dict):
        known_ingredients = ingredient_dict.keys()
        new_ing_dict = {}
        for sent in output_sents:
            foods_in_sent = []
            for food in self.known_food_list:
                if food in sent.split() and food in self.probDictAmt and food not in known_ingredients:
                    amt = self.returnQuant(food)
                    units = self.returnUnit(food)
                    ingredient_dict[food] = [units, amt]
                    new_ing_dict[food] = [units, amt]
                    foods_in_sent.append(food)
        for k,v in new_ing_dict.items():
            print(k, v)
        return ingredient_dict

    def print_recipe(self, ingredient_dict, output_sents):
        print()
        print("Insert title here")
        print()
        print("Ingredients!")
        for k,v in ingredient_dict.items():
            if (len(v) > 1):
                print(v[1], v[0], k)
            elif not v:
                print(k)
            else:
                print(v, k)

        print()
        print("Instructions")
        for sentence in output_sents:
            print(sentence)

        print("Bake until done.")

    def generate_recipe(self, match_ingredients_to_instructions = False):
        ingredient_dict = self.get_ingredients_from_user()
        output_sents, ingredient_dict = self.generate_output_sentences(ingredient_dict, match_ingredients_to_instructions)
        self.print_recipe(ingredient_dict, output_sents)

    def isfloat(self, value):
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

    def frac_to_float(self, frac_str):
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

    def get_float(self, str):
        '''
        Given a string, converts it to a float
        :param str: can be int, decimal, or fraction (in a string)
        :return: float if conversion possible, None else
        '''
        if self.isfloat(str):
            return float(str)
        frac = self.frac_to_float(str)
        if frac:
            return frac
        return None

def main():
    recipe_generator = RecipeGenerator()
    ui = input("Enter anything but q to continue ")
    while ui != 'q':
        recipe_generator.generate_recipe(True)
        ui = input("Enter anything but q to continue ")

if __name__ == '__main__':
    main()
