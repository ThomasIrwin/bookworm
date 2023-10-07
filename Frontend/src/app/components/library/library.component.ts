import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { Observable } from 'rxjs';
import { NgFor } from '@angular/common';
import { AsyncPipe, JsonPipe } from '@angular/common';

import { Book } from 'src/app/data_model/book.model';

@Component({
  selector: 'app-library',
  templateUrl: './library.component.html',
  styleUrls: ['./library.component.scss'],
  standalone: true,
  imports: [NgFor, AsyncPipe, JsonPipe],
})
export class LibraryComponent {
  books: Observable<Book[]> | undefined;

  readonly ROOT_URL = 'http://localhost:8080/api/v1/library/12345';

  constructor(private http: HttpClient) {
    this.getLibrary();
  }

  getLibrary() {
    this.books = this.http.get<Book[]>(this.ROOT_URL);
  }
}
