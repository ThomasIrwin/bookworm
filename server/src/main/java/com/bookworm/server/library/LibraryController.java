package com.bookworm.server.library;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bookworm.server.library.entities.Book;
import com.bookworm.server.library.services.LibraryService;

@RestController
public class LibraryController {
    private final LibraryService libraryService;

    public LibraryController(LibraryService libraryService) {
        this.libraryService = libraryService;
    }

    @GetMapping("/")
    public List<Book> getUserLibrary() {
        return libraryService.getUserLibrary();
    }

    @GetMapping("/health")
    public String health() {
        return libraryService.checkApplicationHealth();
    }
}
