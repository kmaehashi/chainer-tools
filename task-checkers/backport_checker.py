#!/usr/bin/env python

import argparse
import datetime
from multiprocessing import Pool
import os
import traceback

from github import Github


def check_tbp_issue(issue, repo, bp_issues, interactive, verbose):
    # Check all closed issues labeled with "to-be-backported"

    if verbose:
        print(issue)

    try:
        if issue.pull_request is None:
            # No check needed for issues.
            return

        pr = repo.get_pull(issue.number)
        if not pr.merged:
            # No check needed for unmerged PRs.
            return

        for bp_issue in bp_issues:
            if issue.title.strip() in bp_issue.title.strip():
                break
        else:
            if interactive:
                print('PR #{} (@{}): {}'.format(
                    issue.number, pr.merged_by.login, issue.title))
                return
            msg = ('@{} This pull-request is marked as `to-be-backported`, '
                   'but the corresponding backport PR could not be found. '
                   'Could you check?'.format(pr.merged_by.login))
            issue.create_comment(msg)

    except Exception as e:
        print(str(type(e)), e, issue.user.login,
              issue.number, issue.html_url, traceback.format_exc())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--owner', type=str, default='chainer')
    parser.add_argument('--repo', type=str, default='chainer')
    parser.add_argument('--token', type=str,
                        default=os.environ.get('CHAINER_GITHUB_TOKEN', None))
    parser.add_argument('--days', type=int, default=30)
    parser.add_argument('--processes', type=int, default=4)
    parser.add_argument('--interactive', action='store_true')
    parser.add_argument('--verbose', '-v', action='store_true')
    args = parser.parse_args()

    g = Github(args.token)
    org = g.get_organization(args.owner)
    repo = org.get_repo(args.repo)

    since = datetime.datetime.now() - datetime.timedelta(args.days)
    tbp_issues = repo.get_issues(
        labels=[repo.get_label('to-be-backported')],
        state='closed',
        sort='updated',
        since=since,
    )
    bp_issues = repo.get_issues(
        labels=[repo.get_label('backport')],
        state='all',
        sort='updated',
    )

    count = 0
    p = Pool(processes=args.processes)
    for issue in tbp_issues:
        p.apply_async(check_tbp_issue, (issue, repo, bp_issues, args.interactive, args.verbose))
        count += 1
    p.close()
    print('Found {} issues to check...'.format(count))
    p.join()
