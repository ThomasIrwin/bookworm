package com.bookworm.server;

import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import com.bookworm.server.books.entities.Book;
import com.bookworm.server.books.repository.BookRepository;

@SpringBootApplication
public class ServerApplication {

	public static void main(String[] args) {
		SpringApplication.run(ServerApplication.class, args);
	}

	@Bean
	CommandLineRunner testBookDataCommandLineRunner(BookRepository bookRepo) {
		return args -> {
			Book testBook1 = new Book("Brave New World", "Aldous Huxley", "Prophetic dystopian novel from 1932 about future society");
        	Book testBook2 = new Book("Masters of the Air", "Donald Miller", "Gripping telling of the WWII bomber pilots who braved the skies over Germany");
        	Book testBook3 = new Book("The Rise of Theodore Roosevelt", "Edmund Morris", "Depicts the early life of one of the most influential presidents in U.S. History");
			
			Book testBook4 = new Book("The Rise of Theodore Roosevelt", "Edmund Morris", "Depicts the early life of one of the most influential presidents in U.S. History");
			Book testBook5 = new Book("The Rise of Theodore Roosevelt", "Edmund Morris", "Depicts the early life of one of the most influential presidents in U.S. History");
			Book testBook6 = new Book("The Rise of Theodore Roosevelt", "Edmund Morris", "Depicts the early life of one of the most influential presidents in U.S. History");
			Book testBook7 = new Book("The Rise of Theodore Roosevelt", "Edmund Morris", "Depicts the early life of one of the most influential presidents in U.S. History");
			Book testBook8 = new Book("The Rise of Theodore Roosevelt", "Edmund Morris", "Depicts the early life of one of the most influential presidents in U.S. History");
			Book testBook9 = new Book("The Rise of Theodore Roosevelt", "Edmund Morris", "Depicts the early life of one of the most influential presidents in U.S. History");
			
			bookRepo.save(testBook1);
			bookRepo.save(testBook2);
			bookRepo.save(testBook3);
			bookRepo.save(testBook4);
			bookRepo.save(testBook5);
			bookRepo.save(testBook6);
			bookRepo.save(testBook7);
			bookRepo.save(testBook8);
			bookRepo.save(testBook9);
		};
	}
}
