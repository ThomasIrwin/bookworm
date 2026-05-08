package com.bookworm.server.books.exceptions;

public class NullBookException extends RuntimeException {
    public NullBookException() {
        super("Attempted to save a book with a value of null");
    }
}