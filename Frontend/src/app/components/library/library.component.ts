import { AsyncPipe, NgFor } from "@angular/common";
import { Component } from "@angular/core";
import { Observable } from "rxjs";

import { MatCardModule } from "@angular/material/card";

import { AuthService } from "src/app/services/auth.service";
import { LibraryService } from "src/app/services/library.service";
import { Book } from "../../../../../DataModel/Book";

import { BookDisplayComponent } from "../book-display/book-display.component";

@Component({
  selector: "app-library",
  templateUrl: "./library.component.html",
  styleUrls: ["./library.component.scss"],
  standalone: true,
  imports: [NgFor, AsyncPipe, MatCardModule, BookDisplayComponent],
})
export class LibraryComponent {
  books: Observable<Book[]> | undefined;

  constructor(
    private _lib_service: LibraryService,
    private _auth_service: AuthService
  ) {
    this.setUserLibrary();
  }

  setUserLibrary(): void {
    const user_id: string = this._auth_service.getUserId();
    if (user_id !== "") {
      this.books = this._lib_service.getUserLibrary(user_id);
      console.log("Books: ", this.books);
    } else {
      console.log("No user currently signed in");
    }
  }
}
