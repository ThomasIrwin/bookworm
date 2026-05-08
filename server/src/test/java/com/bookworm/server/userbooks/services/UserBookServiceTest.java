package com.bookworm.server.userbooks.services;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.List;
import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.bookworm.server.books.entities.Book;
import com.bookworm.server.books.services.BookService;
import com.bookworm.server.userbooks.dto.AddBookRequest;
import com.bookworm.server.userbooks.dto.UserBookDTO;
import com.bookworm.server.userbooks.entities.UserBook;
import com.bookworm.server.userbooks.enums.ReadingStatus;
import com.bookworm.server.userbooks.exceptions.UnauthorizedUserBookAccessException;
import com.bookworm.server.userbooks.exceptions.UserBookNotFoundException;
import com.bookworm.server.userbooks.repository.UserBookRepository;
import com.bookworm.server.users.entities.User;
import com.bookworm.server.users.services.UserService;

@ExtendWith(MockitoExtension.class)
class UserBooksServiceTest {

    @Mock
    private UserBookRepository userBookRepo;
    @Mock
    private UserService userService;
    @Mock
    private BookService bookService;

    @InjectMocks
    private UserBooksService userBooksService;

    @Test
    void getAllUserBooks_returnsMappedDTOs() {
        User user = new User();
        user.setAuth0Id("auth0|123");

        Book book = new Book("Clean Code", "Robert Martin", "A book about writing clean code");

        UserBook userBook = new UserBook(user, book, ReadingStatus.IN_PROGRESS);
        userBook.setId(1L);

        when(userBookRepo.findAllByUserAuth0Id("auth0|123")).thenReturn(List.of(userBook));

        List<UserBookDTO> result = userBooksService.getAllUserBooks("auth0|123");

        assertEquals(1, result.size());
        UserBookDTO dto = result.get(0);
        assertEquals(1L, dto.id());
        assertEquals("Clean Code", dto.title());
        assertEquals("Robert Martin", dto.author());
        assertEquals("A book about writing clean code", dto.description());
        assertEquals(ReadingStatus.IN_PROGRESS.getDisplayName(), dto.readingStatus());
    }

    @Test
    void getAllUserBooks_returnsEmptyListWhenNoBooksFound() {
        when(userBookRepo.findAllByUserAuth0Id("auth0|123")).thenReturn(List.of());

        List<UserBookDTO> result = userBooksService.getAllUserBooks("auth0|123");

        assertTrue(result.isEmpty());
    }

    @Test
    void addBookToUserLibrary_savesBookAndUserBook() {
        User user = new User();
        user.setAuth0Id("auth0|123");

        AddBookRequest request = new AddBookRequest("Clean Code", "Robert Martin", "A coding book",
                ReadingStatus.IN_PROGRESS);

        when(userService.getUser("auth0|123")).thenReturn(user);
        when(userBookRepo.findAllByUserAuth0Id("auth0|123")).thenReturn(List.of());

        userBooksService.addBookToUserLibrary(request, "auth0|123");

        ArgumentCaptor<Book> bookCaptor = ArgumentCaptor.forClass(Book.class);
        verify(bookService).saveBook(bookCaptor.capture());
        assertEquals("Clean Code", bookCaptor.getValue().getTitle());

        ArgumentCaptor<UserBook> userBookCaptor = ArgumentCaptor.forClass(UserBook.class);
        verify(userBookRepo).save(userBookCaptor.capture());
        assertEquals(user, userBookCaptor.getValue().getUser());
        assertEquals(ReadingStatus.IN_PROGRESS, userBookCaptor.getValue().getStatus());
    }

    @Test
    void deleteBookFromUserLibrary_throwsUserBookNotFoundExceptionWhenBookDoesNotExist() {
        when(userBookRepo.findById(99L)).thenReturn(Optional.empty());

        assertThrows(UserBookNotFoundException.class,
                () -> userBooksService.deleteBookFromUserLibrary(99L, "auth0|123"));
    }

    @Test
    void deleteBookFromUserLibrary_throwsUnauthorizedExceptionWhenUserDoesNotOwnBook() {
        User owner = new User();
        owner.setAuth0Id("auth0|owner");

        UserBook userBook = new UserBook(owner, new Book(), ReadingStatus.IN_PROGRESS);
        userBook.setId(1L);

        when(userBookRepo.findById(1L)).thenReturn(Optional.of(userBook));

        assertThrows(UnauthorizedUserBookAccessException.class,
                () -> userBooksService.deleteBookFromUserLibrary(1L, "auth0|intruder"));
    }

    @Test
    void deleteBookFromUserLibrary_deletesBookWhenAuthorized() {
        User user = new User();
        user.setAuth0Id("auth0|123");

        UserBook userBook = new UserBook(user, new Book(), ReadingStatus.IN_PROGRESS);
        userBook.setId(1L);

        when(userBookRepo.findById(1L)).thenReturn(Optional.of(userBook));

        userBooksService.deleteBookFromUserLibrary(1L, "auth0|123");

        verify(userBookRepo).deleteById(1L);
    }
}