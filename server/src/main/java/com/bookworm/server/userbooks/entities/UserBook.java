package com.bookworm.server.userbooks.entities;

import java.time.LocalDateTime;

import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import com.bookworm.server.books.entities.Book;
import com.bookworm.server.userbooks.enums.ReadingStatus;
import com.bookworm.server.users.entities.User;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.EnumType;
import jakarta.persistence.Enumerated;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;

@Entity
@Table(name = "user_books")
public class UserBook {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "user_id", nullable = false)
    private User user;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "book_id", nullable = false)
    private Book book;

    @Enumerated(EnumType.STRING)
    @Column(nullable = false)
    private ReadingStatus readingStatus;

    private Integer currentPage = 0;
    private LocalDateTime startedReadingAt;
    private LocalDateTime finishedReadingAt;
    private LocalDateTime addedToShelfAt;

    @Column(length = 3000)
    private String personalNotes;

    private Integer rating; // 1-5 stars

    @CreationTimestamp
    private LocalDateTime createdAt;

    @UpdateTimestamp
    private LocalDateTime updatedAt;

    // Constructors
    public UserBook() {
    }

    public UserBook(User user, Book book, ReadingStatus status) {
        this.user = user;
        this.book = book;
        this.readingStatus = status;
        this.addedToShelfAt = LocalDateTime.now();
    }

    // Getters & Setters
    public Long getId() {
        return id;
    }

    public void setId(Long id) {
        this.id = id;
    }

    public User getUser() {
        return user;
    }

    public void setUser(User user) {
        this.user = user;
    }

    public Book getBook() {
        return book;
    }

    public void setBook(Book book) {
        this.book = book;
    }

    public ReadingStatus getStatus() {
        return readingStatus;
    }

    public void setStatus(ReadingStatus status) {
        this.readingStatus = status;
    }

    public Integer getCurrentPage() {
        return currentPage;
    }

    public void setCurrentPage(Integer currentPage) {
        this.currentPage = currentPage;
    }

    public LocalDateTime getStartedReadingAt() {
        return startedReadingAt;
    }

    public void setStartedReadingAt(LocalDateTime startedReadingAt) {
        this.startedReadingAt = startedReadingAt;
    }

    public LocalDateTime getFinishedReadingAt() {
        return finishedReadingAt;
    }

    public void setFinishedReadingAt(LocalDateTime finishedReadingAt) {
        this.finishedReadingAt = finishedReadingAt;
    }

    public LocalDateTime getAddedToShelfAt() {
        return addedToShelfAt;
    }

    public void setAddedToShelfAt(LocalDateTime addedToShelfAt) {
        this.addedToShelfAt = addedToShelfAt;
    }

    public String getPersonalNotes() {
        return personalNotes;
    }

    public void setPersonalNotes(String personalNotes) {
        this.personalNotes = personalNotes;
    }

    public Integer getRating() {
        return rating;
    }

    public void setRating(Integer rating) {
        this.rating = rating;
    }

    public LocalDateTime getCreatedAt() {
        return createdAt;
    }

    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }

    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }

    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }

}
