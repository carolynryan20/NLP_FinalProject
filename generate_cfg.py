import os 
from nltk.parse import stanford 
from nltk import Tree

os.environ['STANFORD_PARSER'] = 'stanford-parser.jar' 
os.environ['STANFORD_MODELS'] = 'stanford-parser-3.8.0-models.jar'  

parser = stanford.StanfordParser(model_path="englishPCFG.ser.gz") 
sentences = parser.raw_parse_sents(("Hello, this is a test sentence.", "What is this final project?")) 

rules_list = set()
for line in sentences:     
	for sentence in line:         
		t = Tree.fromstring(str(sentence))
		for production in t.productions():
			rules_list.add(production)

print(rules_list)
