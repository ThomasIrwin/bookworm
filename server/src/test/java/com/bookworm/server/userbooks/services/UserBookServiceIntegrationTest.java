package com.bookworm.server.userbooks.services;

import static org.assertj.core.api.Assertions.assertThat;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.boot.testcontainers.service.connection.ServiceConnection;
import org.testcontainers.junit.jupiter.Container;
import org.testcontainers.junit.jupiter.Testcontainers;
import org.testcontainers.postgresql.PostgreSQLContainer;

import com.bookworm.server.books.repository.BookRepository;
import com.bookworm.server.userbooks.dto.AddBookRequest;
import com.bookworm.server.userbooks.enums.ReadingStatus;
import com.bookworm.server.users.entities.User;
import com.bookworm.server.users.repository.UserRepository;

@SpringBootTest
@Testcontainers
class UserBookServiceIntegrationTest {

    @Container
    @ServiceConnection
    static PostgreSQLContainer postgres = new PostgreSQLContainer("postgres:15-alpine");

    @Autowired
    UserBooksService service;
    @Autowired
    UserRepository userRepository;
    @Autowired
    BookRepository bookRepository;

    @Test
    void twoUsersCanBothAddTheSameBook() {
        var alice = userRepository.save(new User("alice"));
        var bob = userRepository.save(new User("bob"));

        var req = new AddBookRequest("123", "Clean Code", "Robert C. Martin",
                "The handbook of agile software craftsmanship", ReadingStatus.IN_PROGRESS);

        service.addBookToUserLibrary(req, alice.getAuth0Id());
        service.addBookToUserLibrary(req, bob.getAuth0Id()); // ← 23505 here

        assertThat(bookRepository.count()).isEqualTo(1);
    }
}