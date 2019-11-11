#!/usr/bin/env python

import argparse
import datetime
from multiprocessing import Pool
import os
import traceback

from github import Github


def check_tbp_issue(issue, repo, bp_issues, interactive, verbose):
    # Check each closed issues labeled with "to-be-backported"
    # bp_issues MUST be desc-sorted by creation date.

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

        found_backport = False
        for bp_issue in bp_issues:
            if bp_issue.created_at < issue.created_at:
                # As the creation date of backport PR should always be newer
                # than that of the original PR, terminate iteration.
                break
            if issue.title.strip() in bp_issue.title.strip():
                found_backport = True
                break
        if not found_backport:
            mention_to = pr.merged_by.login
            if mention_to.endswith('[bot]'):
                mention_to = pr.assignee.login

            if interactive:
                print('PR #{} (@{}): {}'.format(
                    issue.number, mention_to, issue.title))
                return
            msg = ('@{} This pull-request is marked as `to-be-backported`, '
                   'but the corresponding backport PR could not be found. '
                   'Could you check?'.format(mention_to))
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
        sort='created',
        direction='desc',
    )

    count = 0
    p = Pool(processes=args.processes)
    for issue in tbp_issues:
        p.apply_async(check_tbp_issue, (issue, repo, bp_issues, args.interactive, args.verbose))
        count += 1
    p.close()
    print('Found {} issues to check...'.format(count))
    p.join()
