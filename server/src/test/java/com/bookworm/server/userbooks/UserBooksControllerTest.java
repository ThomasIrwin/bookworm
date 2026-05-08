package com.bookworm.server.userbooks;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.doNothing;
import static org.mockito.Mockito.doThrow;
import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.delete;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import java.util.List;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import com.bookworm.server.userbooks.dto.AddBookRequest;
import com.bookworm.server.userbooks.dto.UserBookDTO;
import com.bookworm.server.userbooks.enums.ReadingStatus;
import com.bookworm.server.userbooks.exceptions.UnauthorizedUserBookAccessException;
import com.bookworm.server.userbooks.exceptions.UserBookNotFoundException;
import com.bookworm.server.userbooks.services.UserBooksService;
import com.bookworm.server.users.exceptions.UserNotFoundException;
import com.fasterxml.jackson.databind.ObjectMapper;

@WebMvcTest(UserBooksController.class)
class UserBooksControllerTest {

        @Autowired
        private MockMvc mockMvc;

        @Autowired
        private ObjectMapper objectMapper;

        @MockitoBean
        private UserBooksService userBooksService;

        private static final String AUTH0_ID = "auth0|123";

        // --- GET /userbooks/ ---

        @Test
        void getUserBooks_returns200WithBookList() throws Exception {
                UserBookDTO dto = new UserBookDTO(1L, "Clean Code", "Robert Martin", "A coding book", "Reading");
                when(userBooksService.getAllUserBooks(AUTH0_ID)).thenReturn(List.of(dto));

                mockMvc.perform(get("/userbooks/")
                                .with(jwt().jwt(j -> j.claim("sub", AUTH0_ID))))
                                .andExpect(status().isOk())
                                .andExpect(jsonPath("$[0].title").value("Clean Code"))
                                .andExpect(jsonPath("$[0].author").value("Robert Martin"));
        }

        @Test
        void getUserBooks_returns200WithEmptyList() throws Exception {
                when(userBooksService.getAllUserBooks(AUTH0_ID)).thenReturn(List.of());

                mockMvc.perform(get("/userbooks/")
                                .with(jwt().jwt(j -> j.claim("sub", AUTH0_ID))))
                                .andExpect(status().isOk())
                                .andExpect(jsonPath("$").isEmpty());
        }

        // --- POST /userbooks/add-book ---

        @Test
        void addBookToUserLibrary_returns200WithUpdatedList() throws Exception {
                AddBookRequest request = new AddBookRequest("Clean Code", "Robert Martin", "A coding book",
                                ReadingStatus.IN_PROGRESS);
                UserBookDTO dto = new UserBookDTO(1L, "Clean Code", "Robert Martin", "A coding book", "Reading");

                when(userBooksService.addBookToUserLibrary(any(AddBookRequest.class),
                                eq(AUTH0_ID)))
                                .thenReturn(List.of(dto));

                mockMvc.perform(post("/userbooks/add-book")
                                .with(jwt().jwt(j -> j.claim("sub", AUTH0_ID)))
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(objectMapper.writeValueAsString(request)))
                                .andExpect(status().isOk())
                                .andExpect(jsonPath("$[0].title").value("Clean Code"));
        }

        @Test
        void addBookToUserLibrary_returns404WhenUserNotFound() throws Exception {
                AddBookRequest request = new AddBookRequest("Clean Code", "Robert Martin", "A coding book",
                                ReadingStatus.IN_PROGRESS);

                when(userBooksService.addBookToUserLibrary(any(AddBookRequest.class),
                                eq(AUTH0_ID)))
                                .thenThrow(new UserNotFoundException(AUTH0_ID));

                mockMvc.perform(post("/userbooks/add-book")
                                .with(jwt().jwt(j -> j.claim("sub", AUTH0_ID)))
                                .contentType(MediaType.APPLICATION_JSON)
                                .content(objectMapper.writeValueAsString(request)))
                                .andExpect(status().isNotFound());
        }

        // --- DELETE /userbooks/delete-book/{userBookId} ---

        @Test
        void deleteBookFromUserLibrary_returns204WhenSuccessful() throws Exception {
                doNothing().when(userBooksService).deleteBookFromUserLibrary(1L, AUTH0_ID);

                mockMvc.perform(delete("/userbooks/delete-book/1")
                                .with(jwt().jwt(j -> j.claim("sub", AUTH0_ID))))
                                .andExpect(status().isNoContent());
        }

        @Test
        void deleteBookFromUserLibrary_returns404WhenBookNotFound() throws Exception {
                doThrow(new UserBookNotFoundException(99L))
                                .when(userBooksService).deleteBookFromUserLibrary(99L, AUTH0_ID);

                mockMvc.perform(delete("/userbooks/delete-book/99")
                                .with(jwt().jwt(j -> j.claim("sub", AUTH0_ID))))
                                .andExpect(status().isNotFound());
        }

        @Test
        void deleteBookFromUserLibrary_returns403WhenUserDoesNotOwnBook() throws Exception {
                doThrow(new UnauthorizedUserBookAccessException(1L, "auth0|owner", AUTH0_ID))
                                .when(userBooksService).deleteBookFromUserLibrary(1L, AUTH0_ID);

                mockMvc.perform(delete("/userbooks/delete-book/1")
                                .with(jwt().jwt(j -> j.claim("sub", AUTH0_ID))))
                                .andExpect(status().isForbidden());
        }
}