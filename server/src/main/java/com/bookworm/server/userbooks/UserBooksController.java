package com.bookworm.server.userbooks;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.lang.NonNull;
import org.springframework.security.core.Authentication;
import org.springframework.security.oauth2.server.resource.authentication.JwtAuthenticationToken;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import com.bookworm.server.userbooks.dto.AddBookRequest;
import com.bookworm.server.userbooks.dto.UserBookDTO;
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
        String auth0Id = extractAuth0Id(auth);

        List<UserBookDTO> bookList = userBooksService.getAllUserBooks(auth0Id);
        return ResponseEntity.ok(bookList);
    }

    @PostMapping("/add-book")
    public ResponseEntity<List<UserBookDTO>> addBookToUserLibrary(
            @RequestBody AddBookRequest book,
            Authentication auth) {

        String auth0Id = extractAuth0Id(auth);

        List<UserBookDTO> bookList = userBooksService.addBookToUserLibrary(book, auth0Id);
        return ResponseEntity.ok(bookList);
    }

    @DeleteMapping("/delete-book/{userBookId}")
    public ResponseEntity<Void> deleteBookFromUserLibrary(@NonNull @PathVariable Long userBookId, Authentication auth) {
        String auth0Id = extractAuth0Id(auth);

        userBooksService.deleteBookFromUserLibrary(userBookId, auth0Id);
        return ResponseEntity.status(HttpStatus.NO_CONTENT).build();
    }

    private String extractAuth0Id(Authentication auth) {
        return ((JwtAuthenticationToken) auth).getToken().getClaimAsString("sub");
    }
}
