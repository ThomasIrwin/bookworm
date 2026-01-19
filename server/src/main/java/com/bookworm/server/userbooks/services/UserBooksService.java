package com.bookworm.server.userbooks.services;

import java.util.ArrayList;
import java.util.List;

import org.springframework.stereotype.Service;

import com.bookworm.server.books.entities.Book;
import com.bookworm.server.userbooks.entities.UserBook;
import com.bookworm.server.userbooks.enums.ReadingStatus;
import com.bookworm.server.users.entities.User;

@Service
public class UserBooksService {

    public UserBooksService() {
        // TODO inject UserBookRepository into this service, once it's been created
    }

    public List<UserBook> getAllUserBooks(String userId) {
        System.out.println("User ID: " + userId);

        User user = new User(userId, "steve@email.com");
        Book book1 = new Book("Brave New World", "Aldous Huxley",
                "Prophetic dystopian novel from 1932 about future society");

        UserBook userBook = new UserBook(user, book1, ReadingStatus.WANT_TO_READ);

        List<UserBook> bookList = new ArrayList<UserBook>();
        bookList.add(userBook);

        return bookList;
    }
}
