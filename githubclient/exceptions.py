"""Exceptions for the githubclient package."""


class GitHubClientError(Exception):
    """Exception raised when response code is not 2xx."""

    def __init__(self, response_json: dict):
        """Create a new GitHubClientError with custom message."""
        error_details = ''
        if 'errors' in response_json:
            error_details = response_json.get('errors')[0]['message']

        self.message = '{0} {1}'.format(response_json['message'], error_details)
        super().__init__(self.message)
