package com.bookworm.server.books.services;

import java.util.List;
import java.util.Optional;

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

    public Optional<Book> getBook(String title, String author) {
        return bookRepository.findByTitleAndAuthor(title, author);
    }

    public List<Book> getAllBooks() {
        return bookRepository.findAll();
    }

    public String checkApplicationHealth() {
        return "Application is healthy";
    }
}
