import LibraryDataClient from "./library-data-access";
import { Book } from "../../../../../DataModel/Book";


let lib_data_client = new LibraryDataClient();

class LibraryService {
    constructor() {}

    async getUserLibraryData(user_id: string): Promise<Book[] | string> {
        return await lib_data_client.getUserLibraryData(user_id);
    }
}

export default LibraryService;
