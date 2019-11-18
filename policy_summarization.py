import json
import numpy as np
import time, datetime
import argparse
import func_timeout
import itertools
from qm import *

DEBUG = True

def get_trace_limit(filename):
    # These are the capped # of traces used for the kcm eval -- gives us a decent number of state/action pairs
    TRACES = {
        'blocksworld-new': 1000,
        'ex-blocksworld': 1000,
        'elevators': 1000,
        'triangle-tireworld': 1000,
        'traffic-light': 10
    }

    dom = filename.split('/')[1]

    return TRACES[dom]

class Policy(object):
    predicate_list = None
    predicate_count = -1
    states = set()
    actions = set()
    transition_counts = {} # Dict[State str][Action str] = TransitionCount int
    state_actions = {} # Dict[State str] = [Action str, Action str]
    quinemccluskey = None

    def __init__(self, filename):
        self.load_from_json_abm(filename)

    def load_from_json_abm (self, filename):
        with open(filename) as json_file:
            data = json.load(json_file)
            self.predicate_list = data['fluents']
            self.predicate_count = len(self.predicate_list)
            for trace_id in list(data['traces'].keys())[:get_trace_limit(filename)]:

                # Add actions to action set
                # Add states to state set
                # Add (state,action) pairs to transition_counts
                for i in range(0, len(data['traces'][trace_id]['action'])):
                    # Actions
                    action = data['traces'][trace_id]['action'][i]
                    self.actions.add(action)

                    # States
                    state = np.zeros(self.predicate_count, dtype=int)
                    tmp_state = data['traces'][trace_id]['state'][i]
                    for j in range(0, self.predicate_count):
                        if self.predicate_list[j] in tmp_state:
                            state[j] = 1
                    state = str(list(state))
                    self.states.add(state)
                    # Transition Counts
                    if (state, action) in self.transition_counts.keys():
                        self.transition_counts[(state,action)] += 1
                    else:
                        self.transition_counts[(state, action)] = 1

                    # Create dict of states with actions as entries
                    if state in self.state_actions.keys():
                        self.state_actions[state].add(action)
                    else:
                        self.state_actions[state] = set()
                        self.state_actions[state].add(action)

    #################################
    '''
    Question: What do you do?
    Type: 'list_actions'
    List NLP descriptions for each action
    '''
    ################################
    def what_do_you_do(self):
        return self.actions


    #################################
    '''
    Question: When will you {action_list}?
    Type: 'action_summary'
    Find state clusters where action_list elements are the most probable action
    '''
    #################################

    # Helper function for identify_action_clusters
    def get_most_probable_action(self,state):
        '''
          state - State object
          return - Tuple of max action (#, Action), action_counts dict
        '''
        counts = {}
        max_count = (0, None)
        for action in self.state_actions[state]:
            count = self.transition_counts[(state,action)]
            counts[action] = count
            if count > max_count[0]:
                max_count = (count, action)
        return max_count, counts


    def identify_action_clusters(self, state_list = None):
        # Given graph, return a list of state clusters where particular actions are executed
        # USE CASE: when will you do X?

        # Find top-1 action for each state, remove all other edges from graph
        # For each known action... make a state-cluster
        #   * Iterate through all graph edges, looking for action label matching target action
        #     * Remove matching edges from edge list and add origin state to current_action_cluster
        #

        if state_list is None: state_list = self.states

        action_clusters = {} # Key=Action_name, Value=list of states

        for state in state_list:
            action, _ = self.get_most_probable_action(state)
            if action[1] is None: continue
            # TODO: Can set tiers of answers: "Always / Mostly / Sometimes / Rarely" corresponding to probability thresholds
            action_str = action[1]
            if action_str not in action_clusters: action_clusters[action_str] = []
            action_clusters[action_str].append(state)

        return action_clusters

    def get_predicates(self, state, predicate_subset = None):
        predicates = []
        state = state.replace(",", "")
        state = list(state[1:-1].split(" "))
        assert (len(state) == len(self.predicate_list))

        for char in state:
            if char == "0":
                predicates.append(0)
            elif char == "1":
                predicates.append(1)
        predicate_list = self.predicate_list
        if predicate_subset != None:
            predicates = [predicates[i] for i in predicate_subset]
            predicate_list = [predicate_list[i] for i in predicate_subset]
        return predicates, predicate_list

    def perform_boolean_minimization(self, master_predicate_list, include_minterms, exclude_minterms):
        '''
        # Runs Quine-McCluskey algorithm on set of minterms
        # Args:
        #   master_predicate_list - list of possible predicates: e.g., [p1, p2, p3, ..., pn]
        #   minterms - list of predicate truth values -- e.g., [ 10010, 01010, 01111 ] -- for each included state.
        #     - len(minterms[0]) == len(master_predicate_list)
        # Returns:
        #   Minimized boolean expression: e.g., [ [True, None, None, False, None], [False, False, None, True, None] ]

        # TODO: Possible optimization by minimizing the master_predicate_list size before running Quine-McCluskey
        '''
        if DEBUG:
            print ('Include: %d, Exclude: %d' % (len(include_minterms), len(exclude_minterms)))
            print ('Include: %s' % include_minterms)
            print ('Exclude: %s' % exclude_minterms)

        qm_minimization = qm(ones=include_minterms, zeros=exclude_minterms)

        return qm_minimization, master_predicate_list


    def solve_for_state_description_cover(self, state_list, total_state_list=None):
        '''
        # Solves for the best covering set of predicates that describes a list of states

        ##### ARGS #####
        state_list : List of states to include in description
        total_state_list : List of states to consider in cover solution

        '''
        include_table = {}
        exclude_table = {}
        dc_table = {}

        positive_minterms = []
        negative_minterms = []
        dc_minterms = []

        predicates_list = self.predicate_list

        # total state list: all states
        if total_state_list is None:
            total_state_list = self.states
        nonspec_is_negative = False

        # NOT FAITHFUL TO ORIGINAL IMPLEMENTATION
        predicate_subset = []
        # print ("Predicate list: " + str(predicates_list))
        # print ("Len predicates: " + str(len(predicates_list)))
        for idx in range(0,len(predicates_list)):
            tmp_predicate = None
            for state in total_state_list:
                state = list(state[1:-1].split(" "))
                if tmp_predicate == None:
                    tmp_predicate = state[idx]
                elif tmp_predicate != state[idx]:
                    predicate_subset.append(idx)
                    break

        qm_predicate_subset = [self.predicate_list[idx] for idx in predicate_subset]
        self.quinemccluskey = QM(qm_predicate_subset)


        for state in total_state_list:
            predicates, predicates_list = self.get_predicates(state, predicate_subset)  # List of boolean values
            val = 0
            for idx in range(len(predicates)):
                val |= predicates[idx] << idx

            if state in state_list:
                if val not in include_table:
                    include_table[val] = 1
            else:
                if val not in exclude_table:
                    exclude_table[val] = 1

        binary_strings = ["".join(seq) for seq in itertools.product("01", repeat=len(predicate_subset))]

        for binary_string in binary_strings:
            val = 0
            for idx in range(0, len(binary_string)):
                val |= int(binary_string[idx]) << idx

            if val not in include_table and val not in exclude_table:
                dc_table[val] = 1

        dc_minterms = dc_table.keys()

        # # Collect all minterms
        positive_minterms = include_table.keys()
        for minterm in include_table.keys():
            # print "Added positive minterm: %s (%s)" % (str(minterm), b2s(minterm,len(predicates_list)))
            if minterm in exclude_table.keys():
                print ("WARNING: positive minterm found in negative minterm table. Removing from negative minterm table.")  # Minterms can't be positive and negative.
                del exclude_table[minterm]


            if nonspec_is_negative is True:
                negative_minterms = [i for i in xrange(2**len(predicates))]
                for minterm in positive_minterms:
                    negative_minterms.remove(minterm)
            else:
                negative_minterms = exclude_table.keys()
        if DEBUG:
            print ("Negative minterms " + str(negative_minterms))

        time1 = datetime.datetime.now()
        # Retrieve minimized formula describing state region:
        # qm_minimization is string in [0,1,X]* that indexes into final_predicate_list
        #   - first element in qm_minimization corresponds to last element of final_predicate_list
        print ("Starting boolean minimization")
        complexity, minterms = self.quinemccluskey.solve(ones = list(positive_minterms), dc= list(dc_minterms))
        resolve = self.quinemccluskey.get_function(minterms)
        print ("RESOLVE " + str(resolve))
        # qm_minimization, qm_predicate_list =
        # final_predicate_minimization = []
        # for minterm in qm_minimization:
        #     final_predicate_minimization.append(minterm[::-1])

        # if DEBUG:
        #     print ("Initial QM Minimization: %s" % qm_minimization[::-1])

        # final_predicate_list = qm_predicate_list
        time2 = datetime.datetime.now()
        time_diff = time2-time1

        # if DEBUG:
        #     print ("Final QM Minimization: %s" % final_predicate_minimization)
        #     print ("Predicates: %s" % str(predicates_list))

        # state_description = (final_predicate_minimization, final_predicate_list)
        return (resolve, resolve), time_diff.total_seconds()

    def solve_for_state_description(self, state_list, total_state_list=None):
        '''
        state_list - List of states to describe
        total_state_list - List of states to consider when forming cover
        '''

        # Get predicate explanations for action region
        cover, time_tmp = self.solve_for_state_description_cover(state_list = state_list, total_state_list = total_state_list)
        explanations = []

        values, predicate_subset_list = cover
        for clause in values:
            clause_explanation = []
            for idx, predicate_value in enumerate(clause):
                if predicate_value == '1':   clause_explanation.append(predicate_subset_list[idx])
                elif predicate_value == '0':  clause_explanation.append("Not " + predicate_subset_list[idx])

        clause_summary = ' and '.join(clause_explanation)
        if clause_summary not in explanations:
            explanations.append(clause_summary)

        return ' ---or--- '.join(explanations), time_tmp

    def generate_action_cluster_descriptions(self, state_list, action_list=None, threshold=5):
        '''
        @param state_list list of states to include when summarizing action policy
        @param threshold Maximum number of action clusters to include in summary
        '''
        action_clusters = self.identify_action_clusters(state_list)

        '''
        Build explanations for each state list
        '''
        descriptions = {}

        # action clusters: action_clusters[action_str] = [state1, state2]
        for action_type in action_clusters:
            if action_type in action_list or action_list == []:
                descriptions[action_type] = self.solve_for_state_description(state_list=action_clusters[action_type])

        return descriptions

    def describe_action_clusters(self, actions):
        '''
          @param graph Behavioral Graph
          @param argument_text Comma-separated list of action names
        '''
        descriptions = {}

        descriptions = self.generate_action_cluster_descriptions(state_list=self.states, action_list=actions)

        individual_descriptions = []
        for action_name in descriptions:
            individual_descriptions.append('I do %s when %s.' % (action_name, descriptions[action_name]))

        return ' '.join(individual_descriptions)

    #################################
    '''
    Question: What will you do when {state_description}?
    Type: 'state_summary'
    Find action clusters within all states covered by state_description
    '''
    #################################
    def resolve_concept_list_to_state_list(self, true_concepts=[], false_concepts=[]):
        state_list = []

        if len(true_concepts) == 0 and len(false_concepts) == 0: return state_list
        for state in self.states:
            tmp_state = state.replace(",", "")
            state_list_form = list(tmp_state[1:-1].split(" "))

            valid = True
            for concept_id in true_concepts:
                if state_list_form[concept_id] != '1':
                    valid = False
            for concept_id in false_concepts:
                if state_list_form[concept_id] != '0':
                    valid = False
            if valid:
                state_list.append(state)
        return state_list

    def concepts_to_ids(self, concepts):
        predicate_ids = []
        if concepts == []: return predicate_ids

        for concept in concepts:
            predicate_ids.append(self.predicate_list.index(concept))
        return predicate_ids

    def describe_state_behaviors(self, true_predicates, false_predicates):

        true_predicate_ids = self.concepts_to_ids(true_predicates)
        false_predicate_ids = self.concepts_to_ids(false_predicates)

        state_list = self.resolve_concept_list_to_state_list(true_predicate_ids, false_predicate_ids)

        if len(state_list) == 0:
            return ("No states that I've seen match that description.")
        descriptions = self.generate_action_cluster_descriptions(state_list=state_list, action_list=[], threshold=5)

        individual_descriptions = []
        for action_name in descriptions:
            print ("  - I do %s when %s."  % (action_name, descriptions[action_name]))
            individual_descriptions.append('I do %s when %s.' % (action_name, descriptions[action_name]))

        description = ' '.join(individual_descriptions)
        return description

    #################################
    '''
    Question: Why aren't you doing {action}?
    Type: 'difference_summary'
    Find and describe states nearby the current state where {action} is the most probable choice.
    '''
    #################################


parser = argparse.ArgumentParser(description='Policy Summarization.')
parser.add_argument('--filename', type=str,
                   help='filename for stack trace')

parser.add_argument('--timeout', type=int,
                   help='timeout')

args = parser.parse_args()
timeout = args.timeout

action_testing = {
    "domains/blocksworld-new/p1.json": ['pick-up_b5_b4', 'pick-up-from-table_b3'],

    "domains/ex-blocksworld/p1.json": ['pick-up_b5_b4', 'pick-up-from-table_b3'],
    "domains/blocksworld-new/p1.json": [],
    "domains/elevators/p1.json": ['collect_c2_f2_p2', 'go-up_e2_f1_f2'],
    "domains/tiny-triangle-tireworld/p1.json": [],
    "domains/traffic-light/p1.json": ['PHASE_NS_GREEN', 'PHASE_NSL_GREEN'],
    "domains/triangle-tireworld/p1.json": ['move-car_l-1-1_l-2-1', 'move-car_l-2-1_l-3-1', 'changetire_l-2-1']
}

predicates_per_problem = {
    "domains/ex-blocksworld/p1.json": [(["on-table(b2)","on-table(b3)","detonated(b2)"], []), (["detonated(b2)", "detonated(b3)", "on(b3 b2)"],[])],
    "domains/ex-blocksworld/p2.json": [],
    "domains/ex-blocksworld/p3.json": [],

    "domains/blocksworld-new/p1.json": [(["on-table(b1)"], [])],
    "domains/blocksworld-new/p2.json": [],
    "domains/blocksworld-new/p3.json": [],

    "domains/elevators/p1.json": [(["have(c2)"], []), (["at(f1 p1)"],[])],
    "domains/elevators/p2.json": [],
    "domains/elevators/p3.json": [],

    "domains/tiny-triangle-tireworld/p1.json": [(["vehicle-at(l-2-1)"], [])],
    "domains/tiny-triangle-tireworld/p2.json": [],
    "domains/tiny-triangle-tireworld/p3.json": [],

    "domains/traffic-light/p1.json": [(["car_in_S-G0_0-7"], []), (["car_in_S-G0_0-7","car_in_W-G0_0-7"],[])],
    "domains/traffic-light/p2.json": [],
    "domains/traffic-light/p3.json": [],

    "domains/triangle-tireworld/p1.json": [(["vehicle-at(l-2-1)"], []), ([],["spare-in(l-2-2)"])],
    "domains/triangle-tireworld/p2.json": [],
    "domains/triangle-tireworld/p3.json": [],
}

if args.filename != None:
    print ("\n\nPROBLEM: " + str(args.filename))
    policy = Policy(args.filename)

    print ("\nWhat do you do? I can " + str(policy.what_do_you_do()))

    # for action in policy.actions:
    for action in action_testing[args.filename]:
        print ("\nWhen do you " + str(action) + "?")
        try:
            print (func_timeout.func_timeout(timeout, policy.describe_action_clusters, args=([action])))
        except func_timeout.exceptions.FunctionTimedOut:
            print ("Query timed out after " + str(timeout) + " seconds.")


    for (true_predicates_statespace, false_predicates_statespace) in predicates_per_problem[args.filename]:
        print ("\nWhat do you do when " + str(true_predicates_statespace) + " and none of " + str(false_predicates_statespace) + " ? ")
        try:
            print ("I " + str(func_timeout.func_timeout(timeout, policy.describe_state_behaviors, args=(true_predicates_statespace, false_predicates_statespace))))
        except func_timeout.exceptions.FunctionTimedOut:
            print ("Query timed out after " + str(timeout) + " seconds.")
