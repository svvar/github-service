"""Exceptions for the githubclient package."""


class UserNotFoundError(Exception):
    """Exception raised when a user is not found on GitHub."""

    def __init__(self, username: str):
        """Create a new UserNotFoundError with custom message."""
        self.message = 'User {0} not found'.format(username)
        super().__init__(self.message)


class RepositoryCreationError(Exception):
    """Exception raised when a repository cannot be created for API token owner."""

    def __init__(self, response_json: dict):
        """Create a new RepositoryCreationError with custom message."""
        error_details = ''
        if 'errors' in response_json:
            error_details = response_json.get('errors')[0]['message']

        self.message = '{0} {1}'.format(response_json['message'], error_details)
        super().__init__(self.message)


class RepositoryDeletionError(Exception):
    """Exception raised when a repository cannot be deleted from API token owner's profile."""

    def __init__(self, response_json: dict):
        """Create a new RepositoryDeletionError with custom message."""
        self.message = 'Repository deletion failed. {0}'.format(response_json['message'])
        super().__init__(self.message)


class InvalidAccessTokenError(Exception):
    """Exception raised when the access token in key.ini is not associated with any real profile."""

    def __init__(self):
        """Create a new InvalidAccessTokenError with custom message."""
        self.message = 'Invalid access token. Set a valid access token in key.ini'
        super().__init__(self.message)
