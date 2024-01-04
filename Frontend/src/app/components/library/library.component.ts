import { AsyncPipe, NgFor } from '@angular/common';
import { Component } from '@angular/core';
import { Observable } from 'rxjs';

import { MatCardModule } from '@angular/material/card';

import { AuthService } from 'src/app/services/auth.service';
import { LibraryService } from 'src/app/services/library.service';
import { Book } from '../../../../../DataModel/Book';

@Component({
  selector: 'app-library',
  templateUrl: './library.component.html',
  styleUrls: ['./library.component.scss'],
  standalone: true,
  imports: [NgFor, AsyncPipe, MatCardModule],
})
export class LibraryComponent {
  books: Observable<Book[]> | undefined;

  constructor(
    private lib_service: LibraryService,
    private auth_service: AuthService
  ) {
    this.setUserLibrary();
  }

  setUserLibrary(): void {
    const user_id: string = this.auth_service.getUserId();
    if (user_id !== '') {
      this.books = this.lib_service.getUserLibrary(user_id);
      console.log("Books: ", this.books);
    } else {
      console.log('No user currently signed in');
    }
  }
}
