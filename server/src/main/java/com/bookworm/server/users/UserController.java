package com.bookworm.server.users;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bookworm.server.users.services.UserService;

@RestController
@RequestMapping("/users")
public class UserController {
    private final UserService userService;

    public UserController(UserService userService) {
        this.userService = userService;
    }

    @PostMapping("/me")
    public ResponseEntity<String> getOrSaveCurrentUser(Authentication auth) {
        JwtAuthenticationToken token = (JwtAuthenticationToken) auth;
        String auth0Id = token.getToken().getClaimAsString("sub");

        boolean userWasCreated = userService.ensureUserSaved(auth0Id);
        return userWasCreated
                ? ResponseEntity.status(HttpStatus.CREATED).build()
                : ResponseEntity.status(HttpStatus.OK).build();
    }
}