package com.bookworm.server.users.repository;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

import java.util.Optional;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;

import com.bookworm.server.users.entities.User;

// TODO TestContainer for PSQL spinup/teardown when tests run.

@DataJpaTest
class UserRepositoryTest {

    @Autowired
    private UserRepository userRepository;

    @Test
    void findByAuth0Id_returnsUserWhenExists() {
        User user = new User();
        user.setAuth0Id("auth0|abc");
        userRepository.save(user);

        Optional<User> result = userRepository.findByAuth0Id("auth0|abc");

        assertTrue(result.isPresent());
        assertEquals("auth0|abc", result.get().getAuth0Id());
    }

    @Test
    void findByAuth0Id_returnsEmptyWhenNotExists() {
        Optional<User> result = userRepository.findByAuth0Id("auth0|doesnotexist");

        assertFalse(result.isPresent());
    }

    @Test
    void upsertUser_insertsNewUserAndReturnsNonZero() {
        int result = userRepository.upsertUser("auth0|newuser");

        assertEquals(1, result);
        assertTrue(userRepository.findByAuth0Id("auth0|newuser").isPresent());
    }

    @Test
    void upsertUser_doesNotDuplicateExistingUserAndReturnsZero() {
        final String EXISTING_USER_AUTH0_ID = "auth0|existing";

        userRepository.upsertUser(EXISTING_USER_AUTH0_ID);

        int result = userRepository.upsertUser(EXISTING_USER_AUTH0_ID);

        assertEquals(0, result);
        assertEquals(1, userRepository.findAll().stream()
                .filter(u -> EXISTING_USER_AUTH0_ID.equals(u.getAuth0Id()))
                .count());
    }
}