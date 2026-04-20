package com.bookworm.server.userbooks.exceptions;

public class UnauthorizedUserBookAccessException extends RuntimeException {
    public UnauthorizedUserBookAccessException(Long userBookId, String savedUserAuth0Id, String requestingAuth0Id) {
        super("Unauthorized User (" + requestingAuth0Id + ") trying to access a user book (" + userBookId
                + ") that belongs to " + savedUserAuth0Id);
    }
}
