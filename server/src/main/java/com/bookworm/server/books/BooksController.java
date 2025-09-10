package com.bookworm.server.books;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bookworm.server.books.entities.Book;
import com.bookworm.server.books.services.BookService;

@RestController
@RequestMapping("/books")
public class BooksController {
    private final BookService libraryService;

    public BooksController(BookService libraryService) {
        this.libraryService = libraryService;
    }

    @GetMapping("/")
    public List<Book> getAllBooks() {
        return libraryService.getAllBooks();
    }

    @GetMapping("/health")
    public String health() {
        return libraryService.checkApplicationHealth();
    }
}
