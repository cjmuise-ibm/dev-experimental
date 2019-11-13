import json
from pcca_decorator import *
from pcca import *

def load_from_json_abm (filename):
    with open(filename) as json_file:
        data = json.load(json_file)
        predicate_list = data['fluents']
        print (predicate_list)
        # print (data['traces'])

        print (len(data['traces']))

        return predicate_list

predicate_list = load_from_json_abm('blocksworld-new/p1.json')
main_pcca = PCCA(planning_predicates = predicate_list)
print (main_pcca._planning_predicates)
print (main_pcca.determine_question_type("What do you do") )


#################################
'''
Question: What do you do?
Type: 'list_actions'
List NLP descriptions for each action
'''
################################




#################################
'''
Question: When will you {action_list}?
Type: 'action_summary'
Find state clusters where action_list elements are the most probable action
'''
#################################




#################################
'''
Question: What will you do when {state_description}?
Type: 'state_summary'
Find action clusters within all states covered by state_description
'''
#################################


#################################
'''
Question: Why aren't you doing {action}?
Type: 'difference_summary'
Find and describe states nearby the current state where {action} is the most probable choice.
'''
#################################