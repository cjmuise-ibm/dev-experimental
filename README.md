# dev-experimental

Parameters: 
- Set `TIMEOUT` in `call_summarization.sh`
- Add any new domains to `call_summarization.sh`
- Update the parameters to the query "What will you do when {state_description}?" by adding predicates to the two dictionaries: `true_predicates_per_problem` and `false_predicates_per_problem`. These predicates should be formulated as an array of strings: 
`true_predicates_per_problem =   {
                                "domains/blocksworld-new/p1.json": ["on-table(b1)", "on-table(b2)"],
                                }`


1. Change the parameters as specified above to have a query timeout, and to set the state description.
3. To run benchmarking code, run ./call_summarization.sh.  