import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root',
})
export class LibraryService {
  readonly ROOT_URL = 'http://localhost:8080/api/v1';

  user_id: string = '55555';
  data: any;

  constructor(private http_client: HttpClient) {}

  getUserLibrary() {
    this.data = this.http_client.get(
      this.ROOT_URL + `/library/${this.user_id}`
    );
  }
}
