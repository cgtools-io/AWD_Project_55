# once we have a parser:  correct objects, malformed rows, summary logic etc.
#Parser unit tests
#Feed a valid CSV string → assert it returns the correct list of Transaction objects
#Malformed rows (missing column, bad date) → raise or skip with your chosen error
#Summary logic
#Given a small set of transactions, assert CGT calculations match expected values