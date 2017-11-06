import os 
from nltk.parse import stanford 
from nltk.tokenize import sent_tokenize
from nltk import Tree
from pandas import read_csv

os.environ['STANFORD_PARSER'] = 'stanford-parser.jar' 
os.environ['STANFORD_MODELS'] = 'stanford-parser-3.8.0-models.jar'  

parser = stanford.StanfordParser(model_path="englishPCFG.ser.gz") 

cols = ['title', 'ingredients', 'instructions']
recipes = read_csv("recipes.csv", names=cols, encoding='latin-1')

corpus = []

for i in range(len(recipes.instructions)):
	corpus.append(recipes.instructions.loc[i])


rules_list = set()
count = 0
for recipe in corpus:
	recipe_sents = sent_tokenize(recipe)
	sentences = parser.raw_parse_sents((recipe_sents))
	for line in sentences:     
		for sentence in line:         
			t = Tree.fromstring(str(sentence))
			for production in t.productions():
				rules_list.add(production)
	count += 1
	print("Added rules for recipe #" + str(count))
	

f = open('cfg_rules.txt', 'w')
for item in rules_list:
	f.write(str(item) + '\n') 
