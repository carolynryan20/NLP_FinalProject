import nltk
from pandas import read_csv
import re
from random import randint
import numpy as np
from scipy.stats import norm

def main():
    cols = ['title', 'time', 'ingredients', 'instructions']
    recipes_df = read_csv("recipes.csv", names=cols, encoding='latin-1')
    # can get all columns with recipes_df.title, recipes_df.time, recipes_df.ingredients, recipes_df.instructions

    recipes_df.ingredients[:1]

    #input is dataframe of recipes
    #output is a list of list of list
    #biggest level is the ingredient list for every recipes
    #second level is the ingredient list for a single recipe
    #third and final level is ingredient, which is broken into quantity, amount and ingredient
    def createBigList(recipes_df):
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


    def createProb(bigList):
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


    def returnQuant(probDict,food):
        index = randint(0,len(probDict[food])-1)
        return probDict[food][index]

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

    bigList = createBigList(recipes_df)
    probDict = createProb(bigList)
    print(calcPval(probDict,"egg",10))

if __name__ == '__main__':
    main()
