import { Book } from "../../../DataModel/Book";
import LibraryDataClient from "./library-data-access";


let lib_data_client = new LibraryDataClient();

class LibraryService {
    constructor() {}

    async getUserLibraryData(user_id: string): Promise<Book[] | string> {
        return await lib_data_client.getUserLibraryData(user_id);
    }
}

export default LibraryService;
