package com.bookworm.server.library;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.web.servlet.MockMvc;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.content;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(LibraryController.class)
public class LibraryControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    public void whenGetUserLibraryEndpointCalled_returnsExpectedString() throws Exception {
        mockMvc.perform(get("/"))
                .andExpect(status().isOk())
                .andExpect(content().string("Getting User's Library"));
    }

    @Test
    public void whenHealthEndpointCalled_returnsExpectedString() throws Exception {
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
