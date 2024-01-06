import { HttpClient, HttpParams } from "@angular/common/http";
import { Injectable } from "@angular/core";

import { Observable } from "rxjs";
import { Book } from "../../../../DataModel/Book";


@Injectable({
  providedIn: "root"
})
export class ExploreService {
  readonly ROOT_URL ="http://localhost:8080/api/v1/explore";

  constructor(private _http_client: HttpClient) { }

  getSearchResults(user_input: string): Observable<Book[]> {
    let queryParams = new HttpParams();
    queryParams = new HttpParams().append("input", user_input);

    return this._http_client.get<Book[]>(this.ROOT_URL, { params: queryParams });
  }
}
