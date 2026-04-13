package com.bookworm.server;

import org.springframework.boot.CommandLineRunner;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.Bean;

import com.bookworm.server.books.entities.Book;
import com.bookworm.server.books.repository.BookRepository;
import com.bookworm.server.userbooks.entities.UserBook;
import com.bookworm.server.userbooks.enums.ReadingStatus;
import com.bookworm.server.userbooks.repository.UserBookRepository;
import com.bookworm.server.users.entities.User;
import com.bookworm.server.users.repository.UserRepository;

@SpringBootApplication
public class ServerApplication {

	public static void main(String[] args) {
		SpringApplication.run(ServerApplication.class, args);
	}

	@Bean
	CommandLineRunner testUserBookDataCommandLineRunner(
			UserBookRepository userBookRepo,
			BookRepository bookRepo,
			UserRepository userRepo) {
		return args -> {
			Book braveNewWorld = new Book("Brave New World", "Aldous Huxley",
					"Prophetic dystopian novel from 1932 about future society");
			Book mastersOfTheAir = new Book("Masters of the Air", "Donald Miller",
					"Gripping telling of the WWII bomber pilots who braved the skies over Germany");
			Book theRiseOfTR = new Book("The Rise of Theodore Roosevelt", "Edmund Morris",
					"Depicts the early life of one of the most influential presidents in U.S. History");
			bookRepo.save(braveNewWorld);
			bookRepo.save(mastersOfTheAir);
			bookRepo.save(theRiseOfTR);

			User teddyPerkins = new User("auth0|69b49c925df8736c937da952");
			User daveRogers = new User("auth0|68be52df13abefa8ce4852e5");
			userRepo.save(teddyPerkins);
			userRepo.save(daveRogers);

			// Books for Teddy
			UserBook testUserBook1 = new UserBook(teddyPerkins, braveNewWorld, ReadingStatus.IN_PROGRESS);
			userBookRepo.save(testUserBook1);

			// Books for Dave
			UserBook testUserBook2 = new UserBook(daveRogers, mastersOfTheAir, ReadingStatus.IN_PROGRESS);
			UserBook testUserBook3 = new UserBook(daveRogers, theRiseOfTR, ReadingStatus.FINISHED);
			userBookRepo.save(testUserBook2);
			userBookRepo.save(testUserBook3);
		};
	}
}
