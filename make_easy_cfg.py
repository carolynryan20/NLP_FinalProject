'''
NOT USING THIS DON"T
'''

from pandas import read_csv
from nltk import pos_tag
from nltk.grammar import CFG
from nltk.parse.generate import generate

EXCLUDE = ":;(),.'\""
def construct_cfg():
    cols = ['title', 'ingredients', 'instructions']
    recipes_df = read_csv("recipes.csv", names=cols, encoding='latin-1')

    # preheat_oven_to = re.compile('\s*(\d|/|\\\|\s)+')
    temp_list = []
    verb_list = []
    the_rest_list = []
    for recipe in recipes_df['instructions']:
        # print(recipe)
        instructions = recipe.split(".")
        if 'reheat oven to ' in instructions[0]:
            temp = instructions[0].split('reheat oven to ')[1]
            temp = ''.join(ch for ch in temp if ch not in EXCLUDE)
            if temp not in temp_list and len(temp) > 0:
                temp_list.append(temp)
            instructions.pop(0)
        for instruction in instructions:
            # TODO could add POS tags
            instruction_list = instruction.split()
            pos = pos_tag(instruction_list)
            # print(pos, len(pos))

            if len(pos) > 1 and ('V' in pos[0][1] or 'NNP' in pos[0][1]):
                verb = ''.join(ch for ch in pos[0][0] if ch not in EXCLUDE)
                if verb not in verb_list and len(verb) > 0:
                    verb_list.append(verb)

    print(temp_list)
    print(verb_list)
    # print(the_rest_list)

    easy_cfg = '''
                S -> P INS
                P -> PTOT TEMP PERIOD
                PTOT -> 'Preheat the oven to'
                
                INS -> V DET INGR PERIOD | INS INS
                DET -> 'the'
                INGR -> 'eggs' | 'flour' | 'sugar'
                PERIOD -> '.'
                V -> {}
                TEMP -> {}
               '''

    verb_rule = ""
    for verb in verb_list:
        # easy_cfg += "\nV -> '{}'".format(verb)
        verb_rule += " '{}' |".format(verb)

    temp_rule = ""
    for temp in temp_list:
        # easy_cfg += "\nTEMP -> '{}'".format(temp)
        temp_rule += " '{}' |".format(temp)

    easy_cfg = easy_cfg.format(verb_rule, temp_rule)

    print(easy_cfg)
    with open("easy_cfg.txt", "w") as cfg_file:
        cfg_file.write(easy_cfg)

if __name__ == '__main__':
    print("WE ARE NOT USING THIS PLS STOP")
    # construct_cfg()

    with open("easy_cfg.txt", "r") as cfg_file:
        easy_cfg = cfg_file.read()
    my_easy_cfg = CFG.fromstring(easy_cfg)
    # print(easy_cfg)
    # for sentence in generate(my_easy_cfg, depth = 4):
    #     print(' '.join(sentence))

    print(len(list(generate(my_easy_cfg, depth=10))))
    print(list(generate(my_easy_cfg, depth=10))[164000])