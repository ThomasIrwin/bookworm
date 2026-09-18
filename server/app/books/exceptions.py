class NullBookError(Exception):
    def __init__(self) -> None:
        super().__init__("Attempted to save a book with a value of null")
