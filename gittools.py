import logging
import netrc
import os

import requests


class GitApiUtils(object):
    GIT_API_PREFIX = "https://api.github.com"
    GIT_API_REPOS = "%s/repos" % GIT_API_PREFIX
    GIT_REPO_TREES_URI_PREFIX = "/git/trees"
    GIT_REQUEST_TIMEOUT = 120

    def __init__(self):
        self._github_user = os.getenv('GITHUB_USER', None)
        self._github_password = os.getenv('GITHUB_PASS', None)
        if self._github_user and self._github_password:
            self._credentials = (self._github_user, self._github_password)
        else:
            self._credentials = self._get_credentials_from_netrc()


    def create_tag(self, repo, revision, tag):
        """Create a tag for a specific revision
        
        :param str repo: repository name
        :param str revision:  branch name or commit sha in the repository
        :param str tag: The tag to create (e.g. 'v1.0.0')

        :return str: tag url
        """
        logging.info('Creating tag %(tag)s for repository: %(repo)s, revision: %(revision)s',
                     dict(tag=tag, repo=repo, revision=revision))
        data = {
            "tag": tag,
            "object": revision,
            "message": "release %s" % tag,
            "type": "commit",
        }
        url = "%s/%s/git/tags" % (self.GIT_API_REPOS, repo)
        response = requests.post(url, auth=self._credentials, json=data, timeout=self.GIT_REQUEST_TIMEOUT)
        response.raise_for_status()
        tag_obj = response.json()
        ref_data = {'ref': 'refs/tags/%s' % tag, 'sha': tag_obj.get('sha')}
        ref_url = "%s/%s/git/refs" % (self.GIT_API_REPOS, repo)
        response = requests.post(ref_url, auth=self._credentials, json=ref_data, timeout=self.GIT_REQUEST_TIMEOUT)
        response.raise_for_status()
        return response.json().get('url')
    
    @staticmethod
    def _get_credentials_from_netrc(netrc_path=None):
        '''Get the user credentials from .netrc file'''
        ncfile = netrc.netrc(netrc_path or os.path.expanduser('~/.netrc'))
        credentials = ncfile.authenticators("github.com")
        return credentials[0], credentials[2]