# dev-experimental

Parameters:
- Set `TIMEOUT` in `call_summarization.sh`
- Add any new domains to `call_summarization.sh`
- Update the parameters to the query "When would you {action_name}?" by modifying the dictionary `action_testing`.
- Update the parameters to the query "What will you do when {state_description}?" by adding predicates to the dictionary `predicates_per_problem` (list of pairs of positive / negative predicates). These predicates should be formulated like so:
```
predicates_per_problem = {

  ...

    "domains/elevators/p1.json": [(["have(c2)"], []), (["at(f1 p1)"],[])],

  ...

}
```


1. Change the parameters as specified above to have a query timeout, and to set the query descriptions.
2. To run benchmarking code, run ./call_summarization.sh.  
