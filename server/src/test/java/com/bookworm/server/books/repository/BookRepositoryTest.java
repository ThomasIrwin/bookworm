package com.bookworm.server.books.repository;

import static org.assertj.core.api.Assertions.assertThat;

import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.jdbc.AutoConfigureTestDatabase;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.boot.test.autoconfigure.orm.jpa.TestEntityManager;
import org.springframework.test.context.DynamicPropertyRegistry;
import org.springframework.test.context.DynamicPropertySource;
import org.testcontainers.postgresql.PostgreSQLContainer;

import com.bookworm.server.books.entities.Book;

@DataJpaTest
@AutoConfigureTestDatabase(replace = AutoConfigureTestDatabase.Replace.NONE)
public class BookRepositoryTest {

    static PostgreSQLContainer postgres = new PostgreSQLContainer("postgres:15-alpine");

    @BeforeAll
    static void beforeAll() {
        postgres.start();
    }

    @AfterAll
    static void afterAll() {
        postgres.stop();
    }

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

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

    @Test
    void testFindByTitleAndAuthor_bookExists() {
        testEntityManager.clear();

        Optional<Book> book = testBookRepository.findByTitleAndAuthor("Masters of the Air", "Donald Miller");
        assertThat(book).isPresent();
        assertThat(book.get()).isEqualTo(testBook2);
    }

    @Test
    void testFindByTitleAndAuthor_bookNotFound() {
        Optional<Book> book = testBookRepository.findByTitleAndAuthor("Doesn't exist", "John Doe");
        assertThat(book).isNotPresent();
    }
}
