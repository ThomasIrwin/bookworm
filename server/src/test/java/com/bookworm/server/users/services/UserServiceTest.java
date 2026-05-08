package com.bookworm.server.users.services;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import com.bookworm.server.users.entities.User;
import com.bookworm.server.users.exceptions.UserNotFoundException;
import com.bookworm.server.users.repository.UserRepository;

@ExtendWith(MockitoExtension.class)
class UserServiceTest {

    private final String MOCK_AUTH0_ID = "auth0|123";

    @Mock
    private UserRepository userRepository;

    @InjectMocks
    private UserService userService;

    @Test
    void getUser_returnsCorrectUser() {
        User user = new User();
        user.setAuth0Id(MOCK_AUTH0_ID);

        when(userRepository.findByAuth0Id(MOCK_AUTH0_ID)).thenReturn(Optional.of(user));

        User result = userService.getUser(MOCK_AUTH0_ID);
        assertEquals(user, result);
    }

    @Test
    void getUser_throwsUserNotFoundExceptionWhenUserNotFound() {
        when(userRepository.findByAuth0Id(MOCK_AUTH0_ID)).thenReturn(Optional.empty());

        assertThrows(UserNotFoundException.class, () -> userService.getUser(MOCK_AUTH0_ID));
    }

    @Test
    void ensureUserSaved_returnsTrueWhenUpsertAffectsRows() {
        when(userRepository.upsertUser(MOCK_AUTH0_ID)).thenReturn(1);

        boolean result = userService.ensureUserSaved(MOCK_AUTH0_ID);

        assertTrue(result);
    }

    @Test
    void ensureUserSaved_returnsFalseWhenUpsertAffectsNoRows() {
        when(userRepository.upsertUser(MOCK_AUTH0_ID)).thenReturn(0);

        boolean result = userService.ensureUserSaved(MOCK_AUTH0_ID);

        assertFalse(result);
    }

    @Test
    void ensureUserSaved_callsRepositoryWithCorrectId() {
        when(userRepository.upsertUser("auth0|456")).thenReturn(1);

        userService.ensureUserSaved("auth0|456");

        verify(userRepository).upsertUser("auth0|456");
    }
}