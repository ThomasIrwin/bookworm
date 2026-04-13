package com.bookworm.server.userbooks.dto;

public record UserBookDTO(Long id, String title, String author, String description, String readingStatus) {
}
