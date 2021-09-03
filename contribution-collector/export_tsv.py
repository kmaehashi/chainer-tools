#!/usr/bin/env python

import argparse
from collections import defaultdict
import os
import sys

from github import Github


def log(msg):
    sys.stderr.write(f'{msg}\n')


def find_milestone(repo, milestone):
    for ms in repo.get_milestones(state='all'):
        if milestone.strip() == ms.title.strip():
            return ms


def get_issues(milestone, repo):
    milestone = find_milestone(repo, milestone)
    if milestone is None:
        log('*** WARNING! Milestone could not be found: {}'.format(milestone))
        return []
    issues = repo.get_issues(milestone=milestone, state='closed')
    return issues


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--milestone', type=str, action='append')
    parser.add_argument('--owner', type=str, default='chainer')
    parser.add_argument('--repo', type=str, default='chainer')
    parser.add_argument('--token', type=str, default=os.environ['CHAINER_GITHUB_TOKEN'])
    args = parser.parse_args()

    g = Github(args.token)
    org = g.get_organization(args.owner)
    repo = org.get_repo(args.repo)

    authors = defaultdict(int)
    assignees = defaultdict(int)
    for m in args.milestone:
        log(f'Processing milestone: {m}')
        issues = get_issues(m, repo)
        for issue in issues:
            if issue.assignee is None:
                log(f'Assignee not set: {issue.html_url}')
            else:
                assignee = issue.assignee.login
            print('\t'.join([str(issue.number), issue.user.login, assignee]))
            authors[issue.user.login] += 1
            assignees[assignee] += 1

    print('--------')
    print('ID\tAuthored\tAssigned')
    for user in sorted(set(authors.keys()) | set(assignees.keys())):
        print('\t'.join([user, str(authors[user]), str(assignees[user])]))
