package com.bookworm.server.userbooks.entities;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import org.junit.jupiter.api.Test;

import com.bookworm.server.books.entities.Book;
import com.bookworm.server.userbooks.enums.ReadingStatus;
import com.bookworm.server.users.entities.User;

class UserBookTest {

    @Test
    void noArgConstructor_createsInstanceWithNullFields() {
        UserBook userBook = new UserBook();

        assertNull(userBook.getId());
        assertNull(userBook.getUser());
        assertNull(userBook.getBook());
        assertNull(userBook.getStatus());
    }

    @Test
    void parameterisedConstructor_setsFieldsCorrectly() {
        User user = new User();
        Book book = new Book();

        UserBook userBook = new UserBook(user, book, ReadingStatus.IN_PROGRESS);

        assertEquals(user, userBook.getUser());
        assertEquals(book, userBook.getBook());
        assertEquals(ReadingStatus.IN_PROGRESS, userBook.getStatus());
    }

    @Test
    void setId_andGetId_workCorrectly() {
        UserBook userBook = new UserBook();
        userBook.setId(42L);

        assertEquals(42L, userBook.getId());
    }

    @Test
    void setUser_andGetUser_workCorrectly() {
        User user = new User();
        UserBook userBook = new UserBook();
        userBook.setUser(user);

        assertEquals(user, userBook.getUser());
    }

    @Test
    void setBook_andGetBook_workCorrectly() {
        Book book = new Book();
        UserBook userBook = new UserBook();
        userBook.setBook(book);

        assertEquals(book, userBook.getBook());
    }

    @Test
    void setStatus_andGetStatus_workCorrectly() {
        UserBook userBook = new UserBook();
        userBook.setStatus(ReadingStatus.FINISHED);

        assertEquals(ReadingStatus.FINISHED, userBook.getStatus());
    }
}