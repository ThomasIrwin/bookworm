package com.bookworm.server.library;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import com.bookworm.server.library.entities.Book;
import com.bookworm.server.library.services.LibraryService;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.Arrays;

@WebMvcTest(LibraryController.class)
public class LibraryControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
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
    public void testGetUserLibrary() throws Exception {
        when(libraryService.getUserLibrary()).thenReturn(Arrays.asList(testBook1, testBook2));

        mockMvc.perform(get("/"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$").isArray())
                .andExpect(jsonPath("$.length()").value(2))
                .andExpect(jsonPath("$[0].title").value("Brave New World"))
                .andExpect(jsonPath("$[0].author").value("Aldous Huxley"))
                .andExpect(jsonPath("$[1].title").value("Masters of the Air"))
                .andExpect(jsonPath("$[1].author").value("Donald Miller"));
    }

    @Test
    public void whenHealthEndpointCalled_returnsExpectedString() throws Exception {
        when(libraryService.checkApplicationHealth())
            .thenReturn("Application is healthy");
        
        mockMvc.perform(get("/health"))
                .andExpect((status().isOk()))
                .andExpect(content().string("Application is healthy"));
    }

    @Test
    public void whenNonExistantEndpointCalled_returnsNotFound() throws Exception {
        mockMvc.perform(get("/nonexistent"))
                .andExpect(status().isNotFound());
    }
}
