"""GitHub API client implementation."""
import configparser

import requests

from githubclient.exceptions import (
    InvalidAccessTokenError,
    RepositoryCreationError,
    RepositoryDeletionError,
    UserNotFoundError,
)


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
        self.url = 'https://api.github.com'
        self._user = self._get_username_for_key()  # (Task: storing some retrieved data locally)

    def get_user_info(self, username: str):
        """
        Fetch user information for a given username.

        :param username:
        :return: dict with all information about the user

        :raises: UserNotFoundError if user is not found
        """
        response = requests.get(
            '{0}/users/{1}'.format(self.url, username),
            timeout=1,
        )

        if response.status_code != requests.status_codes.codes.OK:
            raise UserNotFoundError(username)
        return response.json()

    def get_user_repos(self, username: str):
        """
        Fetch all repositories of a user.

        :param username: username whose repositories are to be fetched
        :return: list of repository names

        :raises: UserNotFoundError if user is not found
        """
        response = requests.get(
            '{0}/users/{1}/repos'.format(self.url, username),
            timeout=1,
        )

        if response.status_code != requests.status_codes.codes.OK:
            raise UserNotFoundError(username)

        return [repo['name'] for repo in response.json()]

    def create_new_repo(self, repo_name: str, description: str = None, private: bool = False):
        """
        Create a new repository for the owner of the GitHub API key in key.ini .

        :param repo_name: name of the repository to be created
        :param description: description of the repository
        :param private: privacy setting

        :return: url of the created repository

        :raises: RepositoryCreationError if repository creation fails
        """
        response = requests.post(
            '{0}/user/repos'.format(self.url),
            json={'name': repo_name, 'description': description, 'private': private},
            headers={'Authorization': 'Bearer {0}'.format(self._api_key)},
            timeout=1,
        )

        if response.status_code != requests.status_codes.codes.CREATED:
            raise RepositoryCreationError(response.json())

        return response.json()['html_url']

    def delete_repo(self, repo_name: str):
        """
        Delete a repository from GitHub API key owner's account.

        :param repo_name: repository to be deleted
        :return: True if deletion is successful

        :raises: RepositoryDeletionError if repository deletion fails
        """
        response = requests.delete(
            '{0}/repos/{1}/{2}'.format(self.url, self._user, repo_name),
            headers={'Authorization': 'Bearer {0}'.format(self._api_key)},
            timeout=1,
        )

        if response.status_code != requests.status_codes.codes.NO_CONTENT:
            raise RepositoryDeletionError(response.json())
        return True

    def _get_username_for_key(self):
        """
        Use to fetch the username of the GitHub API key owner.

        :return: username of the GitHub API key owner

        :raises: InvalidAccessTokenError if the access token in key.ini is not associated with any real profile
        """
        response = requests.get(
            '{0}/user'.format(self.url),
            headers={'Authorization': 'Bearer {0}'.format(self._api_key)},
            timeout=1,
        )

        if response.status_code != requests.status_codes.codes.OK:
            raise InvalidAccessTokenError()
        return response.json()['login']
