package com.bookworm.server.library.repository;

import com.bookworm.server.library.entities.Book;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface BookRepository extends JpaRepository<Book, Long> {

    // Return all books on the "To-Read", "Reading", and "Read"  shelf with user ID
    
    List<Book> findByTitleContainingIgnoreCase(String title);
}
