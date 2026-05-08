package com.bookworm.server.exceptions;

import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.http.HttpMethod;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.servlet.resource.NoResourceFoundException;

import com.bookworm.server.userbooks.exceptions.UnauthorizedUserBookAccessException;
import com.bookworm.server.userbooks.exceptions.UserBookNotFoundException;
import com.bookworm.server.users.exceptions.UserNotFoundException;

@WebMvcTest(TestController.class)
public class GlobalExceptionHandlerTest {

    @Autowired
    private MockMvc mockMvc;

    @Test
    void handleUserNotFound_returns404WhenUserNotFoundExceptionThrown() throws Exception {
        mockMvc.perform(
                get("/test/user-not-found")
                        .with(jwt().jwt(j -> j.claim("sub", "auth0|123"))))
                .andExpect(status().isNotFound());
    }

    @Test
    void handleUserBookNotFound_returns404WhenUserBookNotFoundExceptionThrown() throws Exception {
        mockMvc.perform(
                get("/test/user-book-not-found")
                        .with(jwt().jwt(j -> j.claim("sub", "auth0|123"))))
                .andExpect(status().isNotFound());
    }

    @Test
    void handleUnauthorizedUserBookAccess_returns403WhenUnauthorizedUserBookAccessExceptionThrown() throws Exception {
        mockMvc.perform(
                get("/test/unauthorized-user-book-access")
                        .with(jwt().jwt(j -> j.claim("sub", "auth0|123"))))
                .andExpect(status().isForbidden());
    }

    @Test
    void handleNoResourceFound_returns404WhenNoResourceFoundExceptionThrown() throws Exception {
        mockMvc.perform(
                get("/test/no-resource-found")
                        .with(jwt().jwt(j -> j.claim("sub", "auth0|123"))))
                .andExpect(status().isNotFound());
    }

    @Test
    void handleGenericException_throws500WhenGenericExceptionThrown() throws Exception {
        mockMvc.perform(
                get("/test/generic-exception")
                        .with(jwt().jwt(j -> j.claim("sub", "auth0|123"))))
                .andExpect(status().isInternalServerError());
    }
}

@RestController
class TestController {
    @GetMapping("/test/user-not-found")
    public void throwUserNotFound() {
        throw new UserNotFoundException("auth0|123");
    }

    @GetMapping("/test/user-book-not-found")
    public void throwUserBookNotFound() {
        throw new UserBookNotFoundException(1L);
    }

    @GetMapping("/test/unauthorized-user-book-access")
    public void throwUnauthorizedUserBookAccessException() {
        throw new UnauthorizedUserBookAccessException(1L, "auth0|123", "auth0|999");
    }

    @GetMapping("/test/no-resource-found")
    public void throwNoResourceFoundException() throws NoResourceFoundException {
        throw new NoResourceFoundException(HttpMethod.GET, "/test/no-resource-found");
    }

    @GetMapping("/test/generic-exception")
    public void throwGenericException() throws Exception {
        throw new Exception();
    }
}
