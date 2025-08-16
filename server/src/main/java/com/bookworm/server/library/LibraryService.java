package com.bookworm.server.library;

import org.springframework.stereotype.Service;

@Service
public class LibraryService {

    public String getUserLibrary() {
        return "Getting User's Library";
    }

    public String checkApplicationHealth() {
        return "Application is healthy";
    }
    
}
