# -*- coding: utf-8 -*-
import json
import copy
import numpy as np

class State(object):
  def __init__(self, feature_list, predicate_functions):
    self._features = feature_list
    self._predicates = []
    self._predicate_functions = predicate_functions

  def __eq__(self, state):
    if state.__class__ == list:
      return self._features == state
    elif state.__class__ == State:
      try:
        return self._features == state._features
      except ValueError:
        if type(self._features) == np.ndarray:
          return np.array_equal(self._features, state._features)
        else:
          print "%s == %s" % (type(self._features), type(state._features))
          return np.all(self._features == state._features)
    else:
      return str(self) == str(state)

  def get_features(self):
    return self._features

  def get_predicates(self):
    '''
    Returns list of boolean values: one for each predicate function that is applied to this state
    '''
    if self._predicates == []:
      self.compute_predicates(self._predicate_functions)
    return self._predicates, self._predicate_functions

  def compute_predicates(self, predicate_functions):
    self._predicates = []
    self._predicate_functions = []
    for func in predicate_functions:
      self._predicates.append(func(self.get_features()))
      self._predicate_functions.append(func)

  def set_predicates(self, predicate_vals, predicate_funcs):
    self._predicates = copy.copy(predicate_vals)
    self._predicate_functions = copy.copy(predicate_funcs)

  def __ne__(self, state):
    return not self.__eq__(state)

  def __str__(self):
    return json.dumps(self._features)

  def __hash__(self):
    return hash(json.dumps(self._features))
