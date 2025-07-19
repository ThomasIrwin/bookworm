package com.bookworm.server.library;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
public class LibraryController {

    @GetMapping("/")
    public String getUserLibrary() {
        return "Getting User's Library";
    }

    @GetMapping("/health")
    public String health() {
        return "Application is healthy";
    }
}
