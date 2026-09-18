class UserBookNotFoundError(Exception):
    def __init__(self, user_book_id: int) -> None:
        super().__init__(f"Book Not Found For User: {user_book_id}")
        self.user_book_id = user_book_id


class UnauthorizedUserBookAccessError(Exception):
    def __init__(
        self, user_book_id: int, saved_user_auth0_id: str, requesting_auth0_id: str
    ) -> None:
        super().__init__(
            f"Unauthorized User ({requesting_auth0_id}) trying to access a user book "
            f"({user_book_id}) that belongs to {saved_user_auth0_id}"
        )
        self.user_book_id = user_book_id
        self.saved_user_auth0_id = saved_user_auth0_id
        self.requesting_auth0_id = requesting_auth0_id
