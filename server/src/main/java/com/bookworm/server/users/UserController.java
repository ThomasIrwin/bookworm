package com.bookworm.server.users;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.bind.annotation.*;

import com.bookworm.server.users.dto.UserRequest;
import com.bookworm.server.users.entities.User;
import com.bookworm.server.users.repository.UserRepository;

@RestController
@RequestMapping("/user")
public class UserController {
    
    @Autowired
    private UserRepository userRepository;
    
    @PostMapping("/save")
    @Transactional
    public ResponseEntity<User> saveUser(@RequestBody UserRequest userRequest) {
        User user = userRepository.upsertUser(userRequest.getAuth0Id(), userRequest.getEmail());
        return ResponseEntity.ok(user);
    }
}