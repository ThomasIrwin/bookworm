import { Axios } from "axios";

class ExploreDataClient {
  private _axios: Axios;

  constructor() {
    this._axios = new Axios();
  }

  getSearchResults(user_input: string) {
    console.log("getting search results...");
  }
}

export default ExploreDataClient;
