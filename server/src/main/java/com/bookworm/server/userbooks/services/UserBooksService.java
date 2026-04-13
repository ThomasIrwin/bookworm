package com.bookworm.server.userbooks.services;

import java.util.List;

import org.springframework.stereotype.Service;

import com.bookworm.server.books.entities.Book;
import com.bookworm.server.books.repository.BookRepository;
import com.bookworm.server.userbooks.dto.AddBookRequest;
import com.bookworm.server.userbooks.dto.UserBookDTO;
import com.bookworm.server.userbooks.entities.UserBook;
import com.bookworm.server.userbooks.exceptions.UserNotFoundExeption;
import com.bookworm.server.userbooks.repository.UserBookRepository;
import com.bookworm.server.users.entities.User;
import com.bookworm.server.users.repository.UserRepository;

import jakarta.transaction.Transactional;

@Transactional
@Service
public class UserBooksService {
    private final UserBookRepository userBookRepo;
    private final UserRepository userRepo;
    private final BookRepository bookRepo;

    public UserBooksService(UserBookRepository userBookRepo, UserRepository userRepo, BookRepository bookRepo) {
        this.userBookRepo = userBookRepo;
        this.userRepo = userRepo;
        this.bookRepo = bookRepo;
    }

    public List<UserBookDTO> getAllUserBooks(String userAuth0Id) {
        List<UserBookDTO> userBookList = userBookRepo
                .findAllByUserAuth0Id(userAuth0Id)
                .stream()
                .map(userBook -> new UserBookDTO(
                        userBook.getId(),
                        userBook.getBook().getTitle(),
                        userBook.getBook().getAuthor(),
                        userBook.getBook().getDescription(),
                        userBook.getStatus().getDisplayName()))
                .toList();

        return userBookList;
    }

    public List<UserBookDTO> addBookToUserLibrary(AddBookRequest book, String userAuth0Id) {
        User currentUser = userRepo.findByAuth0Id(userAuth0Id).orElseThrow(() -> new UserNotFoundExeption(userAuth0Id));

        Book newBook = new Book(book.title(), book.author(), book.description());
        bookRepo.save(newBook);

        UserBook newUserBook = new UserBook(currentUser, newBook, book.readingStatus());
        userBookRepo.save(newUserBook);

        return getAllUserBooks(userAuth0Id);
    }
}
