package com.bookworm.server.users.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.bookworm.server.users.entities.User;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByAuth0Id(String auth0Id);
    
    @Query(value = """
        INSERT INTO users (auth0id, email) 
        VALUES (:auth0Id, :email) 
        ON CONFLICT (auth0id) 
        DO UPDATE SET email = :email 
        RETURNING id, auth0id, email
        """, nativeQuery = true)
    User upsertUser(@Param("auth0Id") String auth0Id, @Param("email") String email);
}