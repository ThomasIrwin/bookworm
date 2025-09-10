package com.bookworm.server.users.entities;

import java.time.LocalDateTime;
import java.util.ArrayList;
import java.util.List;

import org.hibernate.annotations.CreationTimestamp;
import org.hibernate.annotations.UpdateTimestamp;

import com.bookworm.server.userbooks.entities.UserBook;

import jakarta.persistence.*;

@Entity
@Table(name = "users")
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    @Column(unique = true, nullable = false)
    private String auth0Id;
    
    @Column(unique = true, nullable = false)
    private String email;

    // @CreationTimestamp
    // private LocalDateTime createdAt;

    // @UpdateTimestamp
    // private LocalDateTime updatedAt;

    @OneToMany(mappedBy = "user", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<UserBook> readingShelf = new ArrayList<>();
    
    public User() {}
    
    public User(String auth0Id, String email) {
        this.auth0Id = auth0Id;
        this.email = email;
    }
    
    public Long getId() { return id; }
    public void setId(Long id) { this.id = id; }
    
    public String getAuth0Id() { return auth0Id; }
    public void setAuth0Id(String auth0Id) { this.auth0Id = auth0Id; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }

    // public LocalDateTime getCreatedAt() { return createdAt; }
    // public void setCreatedAt(LocalDateTime createdAt) { this.createdAt = createdAt; }
    
    // public LocalDateTime getUpdatedAt() { return updatedAt; }
    // public void setUpdatedAt(LocalDateTime updatedAt) { this.updatedAt = updatedAt; }
    
    public List<UserBook> getReadingShelf() { return readingShelf; }
    public void setReadingShelf(List<UserBook> readingShelf) { this.readingShelf = readingShelf; }
}