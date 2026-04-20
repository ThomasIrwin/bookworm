package com.bookworm.server.users;

import static org.mockito.Mockito.when;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import com.bookworm.server.users.services.UserService;

@WebMvcTest(UserController.class)
public class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private UserService userService;

    @Test
    void whenUnsavedUserReceived_controllerReturns201StatusCode() throws Exception {
        when(userService.ensureUserSaved("auth0|123"))
                .thenReturn(true);

        mockMvc
                .perform(post("/users/me")
                        .with(jwt().jwt(j -> j.claim("sub", "auth0|123"))))
                .andExpect((status().isCreated()));
    }

    @Test
    void whenSavedUserReceived_controllerReturns200StatusCode() throws Exception {
        when(userService.ensureUserSaved("auth0|123"))
                .thenReturn(false);

        mockMvc
                .perform(post("/users/me")
                        .with(jwt().jwt(j -> j.claim("sub", "auth0|123"))))
                .andExpect((status().isOk()));
    }
}
