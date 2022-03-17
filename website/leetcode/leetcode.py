import requests


def get_leetcode_problemset():
    problems = requests.get('https://leetcode.com/api/problems/algorithms/').json()
    problems['stat_status_pairs'].reverse()
    problemset = []
    for p in problems['stat_status_pairs']:
        name = p['stat']['question__title']
        code = p['stat']['question__title_slug']
        paid = p['paid_only']
        submitted = p['stat']['total_submitted']
        problemset.append([code, name, paid, submitted])
    problemset.sort(key=lambda x: x[3])
    problemset.reverse()
    return problemset


