#!/usr/bin/env python

import argparse
import os

from github import Github
from github.GithubObject import NotSet


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--owner', type=str, required=True)
    parser.add_argument(
        '--user', action='store_true')
    parser.add_argument(
        '--repo', type=str, required=True)
    parser.add_argument(
        '--token', type=str, default=os.environ.get('GITHUB_TOKEN', None))
    parser.add_argument(
        '--commit', type=str, required=True)
    parser.add_argument(
        '--state', type=str, required=True,
        choices=['error', 'failure', 'pending', 'success'])
    parser.add_argument(
        '--target-url', type=str, default=NotSet)
    parser.add_argument(
        '--description', type=str, default=NotSet)
    parser.add_argument(
        '--context', type=str, default=NotSet)
    args = parser.parse_args()

    g = Github(args.token)

    owner = (
        g.get_user(args.owner) if args.user else
        g.get_organization(args.owner))

    repo = owner.get_repo(args.repo)
    commit = repo.get_commit(args.commit)
    commit.create_status(
        state=args.state,
        target_url=args.target_url,
        description=args.description,
        context=args.context,
    )
