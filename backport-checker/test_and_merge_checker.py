#!/usr/bin/env python

import argparse
import datetime
from multiprocessing import Pool
import os
import traceback

from github import Github


def check_tam_issue(issue, repo, grace_days, interactive, verbose):
    # Check all open ssues labeled with "to-be-backported"

    if verbose:
        print(issue)

    try:
        if issue.pull_request is None:
            # No check needed for issues.
            return

        days_passed = (datetime.datetime.now() - issue.updated_at).days
        if days_passed < grace_days:
            # Condone the assignee for now.
            return

        if interactive:
            print('PR #{} (@{}): {} ({} days)'.format(
                issue.number, issue.assignee.login, issue.title, days_passed))
            return
        msg = ('@{} This pull-request is marked as `st:test-and-merge`, '
               'but there were no activities for the last {} days. '
               'Could you check?'.format(issue.assignee.login, days_passed))
        issue.create_comment(msg)

    except Exception as e:
        print(str(type(e)), e, issue.user.login,
              issue.number, issue.html_url, traceback.format_exc())


if __name__ == '__main__':
    # When `--grace-days N` is specified, this script will process PRs without
    # activity for the last N days. It is expected that CI completes and the
    # assignee checks the situation of test failures within N days.
    # Note that this script will add comment (unless `--interactive` is
    # specified), which will be counted as a new activity for the PR.
    # The default N is set to 3.

    parser = argparse.ArgumentParser()
    parser.add_argument('--owner', type=str, default='chainer')
    parser.add_argument('--repo', type=str, default='chainer')
    parser.add_argument('--token', type=str,
                        default=os.environ.get('CHAINER_GITHUB_TOKEN', None))
    parser.add_argument('--grace-days', type=int, default=3)
    parser.add_argument('--interactive', action='store_true')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    g = Github(args.token)
    org = g.get_organization(args.owner)
    repo = org.get_repo(args.repo)
    tam_issues = repo.get_issues(
        labels=[repo.get_label('st:test-and-merge')],
        state='open',
        sort='updated',
    )

    count = 0
    for issue in tam_issues:
        check_tam_issue(
            issue, repo, args.grace_days, args.interactive, args.verbose)
        count += 1
    print('Found {} issues to check'.format(count))
