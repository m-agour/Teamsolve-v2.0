import json

import requests

endpoint = f"https://leetcode.com/graphql"

query = """query 
{ matchedUser(username: "user8808tv") {
username
submitStats: submitStatsGlobal {
acSubmissionNum {
difficulty
count
submissions
}
}
}
}"""

r = requests.post(endpoint, json={"query": query})
if r.status_code == 200:
    print(json.dumps(r.json(), indent=2))
else:
    raise Exception(f"Query failed to run with a {r.status_code}.")
