package com.bookworm.server.users.services;

import org.springframework.stereotype.Service;

import com.bookworm.server.users.entities.User;
import com.bookworm.server.users.exceptions.UserNotFoundException;
import com.bookworm.server.users.repository.UserRepository;

import jakarta.transaction.Transactional;

@Service
public class UserService {
    private UserRepository userRepository;

    public UserService(UserRepository userRepo) {
        this.userRepository = userRepo;
    }

    public User getUser(String auth0Id) {
        return userRepository.findByAuth0Id(auth0Id)
                .orElseThrow(() -> new UserNotFoundException(auth0Id));
    }

    @Transactional
    public boolean ensureUserSaved(String auth0Id) {
        System.out.println("ensureUserSaved(): User ID: " + auth0Id);
        int result = userRepository.upsertUser(auth0Id);

        return result != 0;
    }
}
