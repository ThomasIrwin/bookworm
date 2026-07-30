package com.bookworm.server.userbooks.services;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.bookworm.server.books.entities.Book;
import com.bookworm.server.books.services.BookService;
import com.bookworm.server.userbooks.dto.AddBookRequest;
import com.bookworm.server.userbooks.entities.UserBook;
import com.bookworm.server.userbooks.enums.ReadingStatus;
import com.bookworm.server.userbooks.repository.UserBookRepository;
import com.bookworm.server.users.entities.User;
import com.bookworm.server.users.services.UserService;

@ExtendWith(MockitoExtension.class)
class UserBookServiceMockTest {

        @Mock
        BookService bookService;
        @Mock
        UserBookRepository userBookRepository;
        @Mock
        UserService userService;
        @InjectMocks
        UserBooksService service;

        @Test
        void twoUsersCanBothAddTheSameBook() {
                var alice = new User("auth0|alice");
                var bob = new User("auth0|bob");

                var cleanCode = new Book("123", "Clean Code", "Robert C. Martin",
                                "The handbook of agile software craftsmanship");

                when(userService.getUser("auth0|alice")).thenReturn(alice);
                when(userService.getUser("auth0|bob")).thenReturn(bob);

                // The service returns the library it reads back, not what it saved.
                when(userBookRepository.findAllByUserAuth0Id("auth0|alice"))
                                .thenReturn(List.of(new UserBook(alice, cleanCode, ReadingStatus.IN_PROGRESS)));
                when(userBookRepository.findAllByUserAuth0Id("auth0|bob"))
                                .thenReturn(List.of(new UserBook(bob, cleanCode, ReadingStatus.IN_PROGRESS)));
                when(bookService.saveBook(any(Book.class))).thenReturn(cleanCode);

                var req = new AddBookRequest("123", "Clean Code", "Robert C. Martin",
                                "The handbook of agile software craftsmanship", ReadingStatus.IN_PROGRESS);

                var aliceResult = service.addBookToUserLibrary(req, "auth0|alice");
                var bobResult = service.addBookToUserLibrary(req, "auth0|bob");

                assertThat(aliceResult.get(0).title()).isEqualTo("Clean Code");
                assertThat(bobResult.get(0).title()).isEqualTo("Clean Code");
        }
}