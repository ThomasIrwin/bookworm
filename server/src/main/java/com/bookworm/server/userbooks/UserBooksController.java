package com.bookworm.server.userbooks;

import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.bookworm.server.userbooks.entities.UserBook;
import com.bookworm.server.userbooks.services.UserBooksService;

@RestController
@RequestMapping("/userbooks")
public class UserBooksController {
    private final UserBooksService userBooksService;

    public UserBooksController(UserBooksService userBooksService) {
        this.userBooksService = userBooksService;
    }

    @GetMapping("/")
    public ResponseEntity<List<UserBook>> getUserBooks(@RequestParam("user_id") String userId) {
        List<UserBook> bookList = userBooksService.getAllUserBooks(userId);
        return ResponseEntity.ok(bookList);
    }
}
