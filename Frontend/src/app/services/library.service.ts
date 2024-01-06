import { Injectable } from "@angular/core";

import { HttpClient } from "@angular/common/http";

import { Observable } from "rxjs";
import { Book } from "../../../../DataModel/Book";

@Injectable({
  providedIn: "root",
})
export class LibraryService {
  readonly ROOT_URL = "http://localhost:8080/api/v1/library";

  constructor(private _http_client: HttpClient) {}

  getUserLibrary(user_id: string): Observable<Book[]> {
    return this._http_client.get<Book[]>(this.ROOT_URL + `/${user_id}`);
  }
}
