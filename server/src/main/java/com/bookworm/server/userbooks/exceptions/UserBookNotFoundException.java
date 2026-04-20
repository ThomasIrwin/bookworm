package com.bookworm.server.userbooks.exceptions;

public class UserBookNotFoundException extends RuntimeException {
    public UserBookNotFoundException(Long userBookId) {
        super("Book Not Found For User: " + userBookId);
    }
}