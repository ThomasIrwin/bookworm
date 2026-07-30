package com.bookworm.server.userbooks.dto;

import com.bookworm.server.userbooks.enums.ReadingStatus;

public record AddBookRequest(String isbn, String title, String author, String description,
                ReadingStatus readingStatus) {
}
