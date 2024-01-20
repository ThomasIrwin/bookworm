import { Book } from "../../../DataModel/Book";
import ExploreDataClient from "./explore-data-access";

class ExploreService {
  private _explore_data_client: ExploreDataClient;
  
  constructor(explore_data_client: ExploreDataClient) {
    this._explore_data_client = explore_data_client;
  }

  async getSearchResults(user_input: string | undefined): Promise<Book[] | string> {
    if (user_input !== undefined) {
      return await this._explore_data_client.getSearchResults(user_input);
    }
    else return "";
  }
}

export default ExploreService;