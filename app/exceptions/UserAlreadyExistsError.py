class UserAlreadyExistsError(Exception):
    """
    Exception raised when attempting to create a user with a username that already exists.

    Attributes:
        username (str): The username that caused the conflict
        message (str): Explanation of the error
    """

    def __init__(self, username: str):
        self.username = username
        self.message = f"User with name '{username}' already exists."
        super().__init__(self.message)

    def __str__(self):
        return self.message
