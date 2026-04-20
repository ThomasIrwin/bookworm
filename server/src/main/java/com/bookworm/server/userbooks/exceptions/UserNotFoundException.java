package com.bookworm.server.userbooks.exceptions;

public class UserNotFoundException extends RuntimeException {
    public UserNotFoundException(String userAuthId) {
        super("User Not Found: " + userAuthId);
    }
}
