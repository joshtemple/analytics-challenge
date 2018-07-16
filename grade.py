"""Batch grader for analytics challenge solution.json files.

To grade, first create a folder called `submissions` containing all
solution.json files, then run this script.

"""

import os
import json
import collections

def normalize(thing):
    """Uses a Counter object to normalize unordered lists"""
    if isinstance(thing, list):
        return collections.Counter(thing)
    else:
        return thing

def compare(answer, solution):
    """Compares a normalized answer to a normalized solution"""
    solution = normalize(solution)
    answer = normalize(answer)
    if answer == solution:
        return True
    else:
        return False

def show(scores):
    """Displays the final scores in a human-readable format"""
    for filename, score in scores.items():
        print('{} ({}/4 points)'.format(filename.rstrip('.json'), score['total']))
        for i, answer in enumerate(list(score.values())[:-1]):
            print('  {}. {}'.format(i + 1, answer))

if __name__ == '__main__':
    with open('solutions.json', 'r') as f:
        solution = json.load(f)

    scores = {}
    for filename in os.listdir('submissions'):
        with open(os.path.join('submissions', filename), 'r') as f:
            submission = json.load(f)
            score = {}
            for question, answer in submission.items():
                if compare(answer, solution[question]):
                    score[question] = 1
                else:
                    score[question] = 0
            score['total'] = sum(score.values())
            scores[filename] = score

    show(scores)
    with open('scores.json', 'w+') as f:
        json.dump(scores, f)
