package com.bookworm.server.userbooks.repository;

import java.util.List;

import org.springframework.data.jpa.repository.JpaRepository;

import com.bookworm.server.userbooks.entities.UserBook;

public interface UserBookRepository extends JpaRepository<UserBook, Long> {
    List<UserBook> findAllByUserAuth0Id(String userAuth0Id);
}
