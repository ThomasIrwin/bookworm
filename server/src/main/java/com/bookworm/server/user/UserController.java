package com.bookworm.server.user;

import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/user")
public class UserController {

    public UserController() {
    }

    @PutMapping("/profile")
    public String saveUser(@RequestParam String accessToken) {
        System.out.println("User Saved: " + accessToken);
        return "User Saved!";
    }
}
