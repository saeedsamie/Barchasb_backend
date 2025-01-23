class UserAlreadyExistsError(Exception):
    """
    Custom exception raised when a user with the same username already exists.
    """

    def __init__(self, username: str):
        self.username = username
        self.message = f"User with name '{username}' already exists."
        super().__init__(self.message)

    def __str__(self):
        return self.message
