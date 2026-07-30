package com.bookworm.server.books.repository;

import java.util.List;
import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import com.bookworm.server.books.entities.Book;

@Repository
public interface BookRepository extends JpaRepository<Book, Long> {
    List<Book> findByTitleContainingIgnoreCase(String title);

    Optional<Book> findByIsbn(String isbn);

    Optional<Book> findByTitleAndAuthor(String title, String author);
}
