package com.bookworm.server.library.services;

import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.Arrays;
import java.util.List;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.bookworm.server.library.entities.Book;
import com.bookworm.server.library.repository.BookRepository;

import static org.assertj.core.api.Assertions.assertThat;

@ExtendWith(MockitoExtension.class)
public class LibraryServiceTest {

    @Mock
    private BookRepository mockBookRepository;

    @InjectMocks
    private LibraryService libraryService;

    private Book testBook1;
    private Book testBook2;

    @BeforeEach
    void setUp() {
        testBook1 = new Book(
            "Brave New World",
            "Aldous Huxley",
            "Prophetic dystopian novel from 1932 about future society");
        testBook1.setId(1L);

        testBook2 = new Book(
            "Masters of the Air",
            "Donald Miller",
            "Gripping telling of the WWII bomber pilots who braved the skies over Germany");
        testBook2.setId(2L);
    }

    @Test
    void testGetUserLibrary() {
        List<Book> expectedBooks = Arrays.asList(testBook1, testBook2);
        when(mockBookRepository.findAll()).thenReturn(expectedBooks);

        List<Book> actualBooks = libraryService.getUserLibrary();

        assertThat(actualBooks).hasSize(2);
        assertThat(actualBooks).containsExactly(testBook1, testBook2);
        verify(mockBookRepository).findAll();
    }
}
