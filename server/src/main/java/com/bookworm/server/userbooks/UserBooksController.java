package com.bookworm.server.userbooks;

import java.util.ArrayList;
import java.util.List;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import com.bookworm.server.books.entities.Book;
import com.bookworm.server.userbooks.entities.UserBook;
import com.bookworm.server.userbooks.enums.ReadingStatus;
import com.bookworm.server.users.entities.User;

@RestController
@RequestMapping("/userbooks")
public class UserBooksController {
    
    @GetMapping("/")
    public ResponseEntity<List<UserBook>> getUserBooks(@RequestParam("user_id") String userId) {

        // PICK UP HERE: WIRE THIS UP TO A SERVICE< REPO, AND SEED SOME DB DATA
        System.out.println("User ID: " + userId);

        User user = new User(userId, "steve@email.com");
        Book book1 = new Book("Brave New World", "Aldous Huxley", "Prophetic dystopian novel from 1932 about future society");

        UserBook userBook = new UserBook(user, book1, ReadingStatus.WANT_TO_READ);

        List<UserBook> bookList = new ArrayList<UserBook>();
        bookList.add(userBook);

        return ResponseEntity.ok(bookList);
    }
}
