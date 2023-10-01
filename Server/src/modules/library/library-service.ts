import LibraryDataClient from "./library-data-access";

let lib_data_client = new LibraryDataClient();

class LibraryService {
    constructor() {}

    getUserLibraryData(user_id: string) {
        return lib_data_client.getUserLibraryData(user_id);
    }
}

export default LibraryService;