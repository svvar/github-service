"""GitHub API client implementation."""
import configparser
from typing import Any, Dict, Optional

import requests

from githubclient.exceptions import GitHubClientError


class GithubClient(object):
    """
    Class to make some actions using GitHub API.

    API key must be added to key.ini file
    """

    def __new__(cls, *args, **kwargs):
        """Implement simple singleton for GithubClient class."""
        if not getattr(cls, '_instance', None):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize GithubClient class."""
        config = configparser.ConfigParser()
        config.read('githubclient/key.ini')

        self._api_key = config['API']['GITHUB_KEY']
        self._auth_header = {'Authorization': 'Bearer {0}'.format(self._api_key)}
        self._url = 'https://api.github.com'
        self._user = self._get_username_for_key()  # (Task: storing some retrieved data locally)

    def get_user_info(self, username: str):
        """
        Fetch user information for a given username.

        :param username:
        :return: dict with all information about the user
        """
        endpoint = '/users/{0}'.format(username)
        return self._make_request(
            'GET',
            endpoint=endpoint,
        ).json()

    def get_user_repos(self, username: str):
        """
        Fetch all repositories of a user.

        :param username: username whose repositories are to be fetched
        :return: list of repository names
        """
        endpoint = '/users/{0}/repos'.format(username)
        response = self._make_request(
            'GET',
            endpoint=endpoint,
        )
        return [repo['name'] for repo in response.json()]

    def create_new_repo(self, repo_name: str, description: str = None, private: bool = False):
        """
        Create a new repository for the owner of the GitHub API key in key.ini .

        :param repo_name: name of the repository to be created
        :param description: description of the repository
        :param private: privacy setting

        :return: url of the created repository
        """
        endpoint = '/user/repos'
        response = self._make_request(
            'POST',
            endpoint=endpoint,
            json={'name': repo_name, 'description': description, 'private': private},
            headers=self._auth_header,
        )

        return response.json()['html_url']

    def delete_repo(self, repo_name: str):
        """
        Delete a repository from GitHub API key owner's account.

        :param repo_name: repository to be deleted
        :return: True if deletion is successful

        """
        endpoint = '/repos/{0}/{1}'.format(self._user, repo_name)
        self._make_request(
            'DELETE',
            endpoint=endpoint,
            headers=self._auth_header,
        )
        return True

    def _get_username_for_key(self):
        """
        Use to fetch the username of the GitHub API key owner.

        :return: username of the GitHub API key owner
        """
        endpoint = '/user'
        response = self._make_request(
            'GET',
            endpoint=endpoint,
            headers=self._auth_header,
        )

        return response.json()['login']

    def _make_request(
        self,
        method: str,
        endpoint: str,
        json: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        """
        Request method for interacting with API.

        :param method: request method
        :param endpoint: URL endpoint for API
        :param json: request body data, defaults to None
        :param headers: request headers, defaults to None

        :return: response

        :raises: GitHubClientError if response code is not 2xx
        """
        response = requests.request(
            method=method,
            url=self._url + endpoint,
            json=json,
            headers=headers,
            timeout=1,
        )

        try:
            response.raise_for_status()
        except requests.HTTPError:
            raise GitHubClientError(response.json())

        return response
