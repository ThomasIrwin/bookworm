import { initializeApp } from "firebase/app";
import { getFirestore, doc, getDoc } from "firebase/firestore";
import { Book } from "../../../../../DataModel/Book";

const firebaseConfig = {
    projectId: "bookworm-f8f51",
    appId: "1:935535190365:web:521b630698d0f5746088b4",
    databaseURL: "https://bookworm-f8f51-default-rtdb.firebaseio.com",
    storageBucket: "bookworm-f8f51.appspot.com",
    apiKey: "AIzaSyApYldBVKBuVqfPiGD3ryxXnZ-vOwK3YK0",
    authDomain: "bookworm-f8f51.firebaseapp.com",
    messagingSenderId: "935535190365",
    measurementId: "G-NVDNX440VT",
};

const app = initializeApp(firebaseConfig);
const db = getFirestore(app);

class LibraryDataClient {
    constructor() {}

    async getUserLibraryData(user_id: string): Promise<Book[] | string> {
        let library: Book[] = [];
        let user = await getDoc(doc(db, "users", `${user_id}`));

        if (user.exists()) {
            const user_lib = user.data().books;
            Object.keys(user_lib).forEach(fs_book => {
                let book: Book = {
                    title: user_lib[fs_book].title,
                    author: user_lib[fs_book].author,
                    pages: user_lib[fs_book].pages,
                    cover_image_url: user_lib[fs_book].cover_image_url
                };

                library.push(book);
            });
            return library;
        }
        else {
            return "";
        }
    }
}

export default LibraryDataClient;
