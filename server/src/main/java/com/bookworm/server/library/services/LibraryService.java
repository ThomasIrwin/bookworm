package com.bookworm.server.library.services;

import org.springframework.stereotype.Service;
import java.util.List;

import com.bookworm.server.library.entities.Book;
import com.bookworm.server.library.repository.BookRepository;

@Service
public class LibraryService {

    private final BookRepository bookRepository;

    public LibraryService(BookRepository bookRepository) {
        this.bookRepository = bookRepository;
    }

    public List<Book> getUserLibrary() {
        return bookRepository.findAll();
    }

    public String checkApplicationHealth() {
        return "Application is healthy";
    }
}
