package com.bookworm.server.userbooks;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bookworm.server.userbooks.dto.AddBookRequest;
import com.bookworm.server.userbooks.dto.UserBookDTO;
import com.bookworm.server.userbooks.exceptions.UserNotFoundExeption;
import com.bookworm.server.userbooks.services.UserBooksService;

@RestController
@RequestMapping("/userbooks")
public class UserBooksController {
    private final UserBooksService userBooksService;

    public UserBooksController(UserBooksService userBooksService) {
        this.userBooksService = userBooksService;
    }

    @GetMapping("/")
    public ResponseEntity<List<UserBookDTO>> getUserBooks(Authentication auth) {
        JwtAuthenticationToken token = (JwtAuthenticationToken) auth;
        String auth0Id = token.getToken().getClaimAsString("sub");
        System.out.println("getUserBooks(): User ID: " + auth0Id);

        List<UserBookDTO> bookList = userBooksService.getAllUserBooks(auth0Id);
        return ResponseEntity.ok(bookList);
    }

    @PutMapping("/add-book")
    public ResponseEntity<List<UserBookDTO>> addBookToUserLibrary(
            @RequestBody AddBookRequest book,
            Authentication auth) {

        JwtAuthenticationToken token = (JwtAuthenticationToken) auth;
        String auth0Id = token.getToken().getClaimAsString("sub");

        try {
            List<UserBookDTO> bookList = userBooksService.addBookToUserLibrary(book, auth0Id);
            return ResponseEntity.ok(bookList);
        } catch (UserNotFoundExeption userNotFoundException) {
            return ResponseEntity.notFound().build();
        } catch (Exception e) {
            return ResponseEntity.status(HttpStatus.INTERNAL_SERVER_ERROR).build();
        }
    }
}
