package com.bookworm.server.users.repository;

import java.util.Optional;

import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import org.springframework.stereotype.Repository;

import com.bookworm.server.users.entities.User;

@Repository
public interface UserRepository extends JpaRepository<User, Long> {
    Optional<User> findByAuth0Id(String auth0Id);

    @Modifying
    @Query(value = """
            INSERT INTO users (auth0id) VALUES (:auth0Id) ON CONFLICT DO NOTHING
            """, nativeQuery = true)
    int upsertUser(@Param("auth0Id") String auth0Id);
}