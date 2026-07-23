package com.bookworm.server.userbooks.services;

import java.util.List;
import java.util.Optional;

import org.springframework.lang.NonNull;
import org.springframework.stereotype.Service;

import com.bookworm.server.books.entities.Book;
import com.bookworm.server.books.services.BookService;
import com.bookworm.server.userbooks.dto.AddBookRequest;
import com.bookworm.server.userbooks.dto.UserBookDTO;
import com.bookworm.server.userbooks.entities.UserBook;
import com.bookworm.server.userbooks.exceptions.UnauthorizedUserBookAccessException;
import com.bookworm.server.userbooks.exceptions.UserBookNotFoundException;
import com.bookworm.server.userbooks.repository.UserBookRepository;
import com.bookworm.server.users.entities.User;
import com.bookworm.server.users.services.UserService;

import jakarta.transaction.Transactional;

@Transactional
@Service
public class UserBooksService {
    private final UserBookRepository userBookRepo;
    private final UserService userService;
    private final BookService bookService;

    public UserBooksService(UserBookRepository userBookRepo, UserService userService, BookService bookService) {
        this.userBookRepo = userBookRepo;
        this.userService = userService;
        this.bookService = bookService;
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
        User currentUser = userService.getUser(userAuth0Id);

        Optional<Book> newBook = bookService.getBook(book.title(), book.author());
        if (newBook.isEmpty()) {
            newBook = Optional.of(new Book(book.title(), book.author(), book.description()));
            bookService.saveBook(newBook.get());
        }

        UserBook newUserBook = new UserBook(currentUser, newBook.get(),
                book.readingStatus());
        userBookRepo.save(newUserBook);

        return getAllUserBooks(userAuth0Id);
    }

    public void deleteBookFromUserLibrary(@NonNull Long userBookId, String userAuth0Id) {
        UserBook userBook = userBookRepo.findById(userBookId)
                .orElseThrow(() -> new UserBookNotFoundException(userBookId));

        String savedUserBookAuth0Id = userBook.getUser().getAuth0Id();
        if (!savedUserBookAuth0Id.equals(userAuth0Id)) {
            throw new UnauthorizedUserBookAccessException(userBookId,
                    savedUserBookAuth0Id, userAuth0Id);
        }

        userBookRepo.deleteById(userBookId);
    }
}
