package com.bookworm.server.users.entities;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNull;

import org.junit.jupiter.api.Test;

public class UserTest {

    @Test
    void noArgConstructor_createsInstanceWithNullFields() {
        User user = new User();

        assertNull(user.getId());
        assertNull(user.getAuth0Id());
    }

    @Test
    void constructorWithParameters_setsFieldsCorrectly() {
        User user = new User("auth0|123");

        assertEquals(user.getAuth0Id(), "auth0|123");
    }

    @Test
    void setId_getIdWorksCorrectly() {
        User user = new User();
        user.setId(42L);

        assertEquals(user.getId(), 42L);
    }

    @Test
    void setAuth0Id_getAuth0IdWorksCorrectly() {
        User user = new User();
        user.setAuth0Id("auth0|999");

        assertEquals(user.getAuth0Id(), "auth0|999");
    }
}
