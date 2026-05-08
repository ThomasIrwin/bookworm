package com.bookworm.server.books.repository;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;

import com.bookworm.server.books.entities.Book;

@DataJpaTest
public class BookRepositoryTest {

    @Autowired
    private TestEntityManager testEntityManager;

    @Autowired
    private BookRepository testBookRepository;

    private Book testBook1;
    private Book testBook2;
    private Book testBook3;

    @BeforeEach
    void setUp() {
        testBook1 = new Book(
                "Brave New World",
                "Aldous Huxley",
                "Prophetic dystopian novel from 1932 about future society");
        testBook2 = new Book(
                "Masters of the Air",
                "Donald Miller",
                "Gripping telling of the WWII bomber pilots who braved the skies over Germany");
        testBook3 = new Book(
                "The Rise of Theodore Roosevelt",
                "Edmund Morris",
                "Depicts the early life of one of the most influential presidents in U.S. History");

        testEntityManager.persistAndFlush(testBook1);
        testEntityManager.persistAndFlush(testBook2);
        testEntityManager.persistAndFlush(testBook3);
    }

    @Test
    void testFindByTitleContainingIgnoreCase() {
        List<Book> books = testBookRepository.findByTitleContainingIgnoreCase("of");

        assertThat(books).hasSize(2);
        assertThat(books)
                .extracting(Book::getTitle)
                .containsExactlyInAnyOrder("Masters of the Air", "The Rise of Theodore Roosevelt");
    }

    @Test
    void testFindByTitleContainingIgnoreCase_caseInsensitive() {
        List<Book> books = testBookRepository.findByTitleContainingIgnoreCase("MASTERS");

        assertThat(books).hasSize(1);
        assertThat(books.get(0).getTitle()).isEqualTo("Masters of the Air");
    }
}
