import axios from "axios";
import dotenv from "dotenv";
import { Book } from "../../../DataModel/Book";

dotenv.config();

const GBOOKS_API_KEY = process.env.GBOOKS_API_KEY;


class ExploreDataClient {

  constructor() {}

  async getSearchResults(user_input: string): Promise<Book[] | string> {
    // Format and store results
    let search_results: Array<Book> = [];
    let results = await axios.get(`https://www.googleapis.com/books/v1/volumes?q=${user_input}&key=${GBOOKS_API_KEY}`);
    if (results) {
      for (let i = 0; i < 6; i++) {
        let book = this.convertToBookFormat(results.data.items[i]);
        search_results.push(book);
      }
      return search_results;
    }
    else {
      return "";
    }
  }

  private convertToBookFormat(book: any): Book {
    let formatted_book: Book = {
      ISBN: book.volumeInfo.industryIdentifiers[0].identifier,
      authors: book.volumeInfo.authors,
      book_id: book.id,
      cover_image: book.volumeInfo.imageLinks.thumbnail.toString(),
      description: book.volumeInfo.description,
      genres: [],
      language: book.volumeInfo.language,
      page_count: book.volumeInfo.pageCount,
      publication_date: this.convertToDate(book.volumeInfo.publishedDate),
      publisher: book.volumeInfo.publisher,
      title: book.volumeInfo.title
    };

    return formatted_book;
  }

  private convertToDate(date: string): Date {
    let date_array: Array<string> = date.split("-");
    let return_date = new Date(Number(date_array[0]), Number(date_array[1]) - 1, Number(date_array[2]));

    return return_date;
  }
}

export default ExploreDataClient;
