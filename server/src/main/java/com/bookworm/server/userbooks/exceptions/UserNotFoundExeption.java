package com.bookworm.server.userbooks.exceptions;

public class UserNotFoundExeption extends RuntimeException {
    public UserNotFoundExeption(String userAuthId) {
        super("User Not Found: " + userAuthId);
    }
}
