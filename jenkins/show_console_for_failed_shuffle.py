import xml.etree.ElementTree
import urllib.request


def get(url):
    return xml.etree.ElementTree.fromstring(urllib.request.urlopen(url).read())

def show(job):
    matrix = get('https://jenkins.preferred.jp/job/chainer/job/{}/api/xml?xpath=/matrixProject/activeConfiguration[color="red"]/url&wrapper=result'.format(job))
    for m in matrix:
        print('open "{}lastBuild/console#footer"'.format(m.text))

if __name__ == '__main__':
    for repo in ['chainer', 'cupy']:
        for branch in ['master', 'stable']:
            job = 'daily_{}_{}-shuffled'.format(branch, repo)
            print('### {}'.format(job))
            show(job)
            print('')
