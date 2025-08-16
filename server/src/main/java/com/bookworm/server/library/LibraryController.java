package com.bookworm.server.library;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class LibraryController {
    private final LibraryService libraryService;

    public LibraryController(LibraryService libraryService) {
        this.libraryService = libraryService;
    }

    @GetMapping("/")
    public String getUserLibrary() {
        return libraryService.getUserLibrary();
    }

    @GetMapping("/health")
    public String health() {
        return libraryService.checkApplicationHealth();
    }
}
