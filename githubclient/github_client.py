
import requests
import configparser


class GithubClient:
    """
    Class to make some actions using GitHub API.
    API key must be added to key.ini file
    """

    def __new__(cls, *args, **kwargs):
        """
        Basic singleton implementation for githubclient class

        """
        if not hasattr(cls, '_instance'):
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        config = configparser.ConfigParser()
        config.read('key.ini')

        self.__api_key = config['API']['GITHUB_KEY']        # GitHub API key from key.ini
        self.url = 'https://api.github.com'                 # GitHub API URL
        self.__user = self.__get_username_for_key()         # GitHub API key owner's username
                                                            # (Task: storing some retrieved data locally)

    def __get_username_for_key(self):
        """
        Used to fetch the username of the GitHub API key owner

        """
        response = requests.get(f'{self.url}/user', headers={'Authorization': f'Bearer {self.__api_key}'})

        if response.status_code != requests.status_codes.codes.OK:
            raise Exception('Invalid API key')
        return response.json()['login']

    def get_user_info(self, username: str):
        """
        Fetches user information for a given username

        :param username:
        :return: dict with all information about the user
        """
        response = requests.get(f'{self.url}/users/{username}')

        if response.status_code != requests.status_codes.codes.OK:
            raise Exception(response.json()['message'])
        return response.json()

    def get_user_repos(self, username: str):
        """
        Fetches all repositories of a user

        :param username: username whose repositories are to be fetched
        :return: list of repository names
        """
        response = requests.get(f'{self.url}/users/{username}/repos')

        if response.status_code != requests.status_codes.codes.OK:
            raise Exception(response.json()['message'])

        repo_names = [r['name'] for r in response.json()]
        return repo_names

    def create_new_repo(self, repo_name: str, description: str = None, private: bool = False):
        """
        Creates a new repository for the owner of the GitHub API key in key.ini

        :param repo_name: name of the repository to be created
        :param description: description of the repository
        :param private: privacy setting

        :return: url of the created repository

        :raises: Exception if repository creation fails
        """

        response = requests.post(f'{self.url}/user/repos', json={'name': repo_name,
                                                                 'description': description,
                                                                 'private': private},
                                 headers={'Authorization': f'Bearer {self.__api_key}'})

        if response.status_code != requests.status_codes.codes.CREATED:
            error_details = ''
            if 'errors' in response.json:
                error_details = response.json()['errors'][0]['message']
            raise Exception(f"{response.json()['message']} {error_details}")
        return response.json()['html_url']

    def delete_repo(self, repo_name: str):
        """
        Deletes a repository from GitHub API key owner's account

        :param repo_name: repository to be deleted
        :return: True if deletion is successful

        :raises: Exception if repository deletion fails
        """

        response = requests.delete(f"{self.url}/repos/{self.__user}/{repo_name}",
                                   headers={'Authorization': f'Bearer {self.__api_key}'})

        if response.status_code != requests.status_codes.codes.NO_CONTENT:
            raise Exception(f'Repository {repo_name} deletion failed. {response.json()["message"]}')
        return True

