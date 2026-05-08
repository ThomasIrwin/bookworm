package com.bookworm.server.books.services;

import java.util.List;

import org.springframework.stereotype.Service;

import com.bookworm.server.books.entities.Book;
import com.bookworm.server.books.exceptions.NullBookException;
import com.bookworm.server.books.repository.BookRepository;

@Service
public class BookService {

    private final BookRepository bookRepository;

    public BookService(BookRepository bookRepository) {
        this.bookRepository = bookRepository;
    }

    // TODO: Remove once ETL pipelines are in place.
    // Book creation is temporarily user-facing until the database is populated.
    public void saveBook(Book book) {
        if (book == null) {
            throw new NullBookException();
        }

        bookRepository.save(book);
    }

    public List<Book> getAllBooks() {
        return bookRepository.findAll();
    }

    public String checkApplicationHealth() {
        return "Application is healthy";
    }
}
