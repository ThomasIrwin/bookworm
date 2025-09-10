package com.bookworm.server.library.entities;

import java.util.Set;

import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import com.bookworm.server.books.entities.Book;

import jakarta.validation.ConstraintViolation;
import jakarta.validation.Validation;
import jakarta.validation.Validator;
import jakarta.validation.ValidatorFactory;

import static org.assertj.core.api.Assertions.assertThat;

public class BookTest {
    
    private Validator validator;

    @BeforeEach
    void setUp() {
        ValidatorFactory validatorFactory = Validation.buildDefaultValidatorFactory();
        validator = validatorFactory.getValidator();
    }

    @Test
    void testValidBook() {
        Book book = new Book(
            "Valid Title",
            "Valid Author",
            "Valid description");
        
        Set<ConstraintViolation<Book>> violations = validator.validate(book);
        
        assertThat(violations).isEmpty();
    }

    @Test
    void testBlankTitle() {
        Book book = new Book("", "Valid Author", "Valid description");
        
        Set<ConstraintViolation<Book>> violations = validator.validate(book);
        
        assertThat(violations).hasSize(1);
        assertThat(violations.iterator().next().getMessage()).isEqualTo("Title is required");
    }

    @Test
    void testBlankAuthor() {
        Book book = new Book("Valid Title", "", "Valid description");
        
        Set<ConstraintViolation<Book>> violations = validator.validate(book);
        
        assertThat(violations).hasSize(1);
        assertThat(violations.iterator().next().getMessage()).isEqualTo("Author is required");
    }

    @Test
    void testNullDescription() {
        Book book = new Book("Valid Title", "Valid Author", null);
        
        Set<ConstraintViolation<Book>> violations = validator.validate(book);
        
        assertThat(violations).isEmpty(); // Description is optional
    }

    @Test
    void testBookConstructorAndGetters() {
        Book book = new Book("Test Title", "Test Author", "Test Description");
        book.setId(1L);
        
        assertThat(book.getTitle()).isEqualTo("Test Title");
        assertThat(book.getAuthor()).isEqualTo("Test Author");
        assertThat(book.getDescription()).isEqualTo("Test Description");
        assertThat(book.getId()).isEqualTo(1L);
    }
}
