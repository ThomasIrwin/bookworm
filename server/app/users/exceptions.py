class UserNotFoundError(Exception):
    def __init__(self, user_auth0_id: str) -> None:
        super().__init__(f"User Not Found: {user_auth0_id}")
        self.user_auth0_id = user_auth0_id
