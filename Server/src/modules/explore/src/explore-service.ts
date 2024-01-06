import ExploreDataClient from "./explore-data-access";


let explore_data_client = new ExploreDataClient();

class ExploreService {
    constructor() {}

    async getSearchResults(user_input: string | undefined) {
      if (user_input !== undefined) {
        explore_data_client.getSearchResults(user_input);
      }
    }
}

export default ExploreService;