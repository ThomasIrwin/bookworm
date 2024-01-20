import { initializeApp } from "firebase/app";
import { DocumentReference, DocumentSnapshot, Query, QuerySnapshot, collection, doc, getDoc, getDocs, getFirestore, query, where } from "firebase/firestore";
import { Book } from "../../../DataModel/Book";

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
    constructor() { }

    async getUserLibraryData(user_id: string): Promise<Book[] | string> {
        let library: Book[] = [];

        const userRef = doc(db, "users", `${user_id}`);
        const libQuery: Query = query(
            collection(db, "libraries"),
            where("user_id", "==", userRef)
        );
        const userLibraryQuerySnapshot: QuerySnapshot = await getDocs(libQuery);

        if (!userLibraryQuerySnapshot.empty) {
            // user_id is unique so first array element is the user's library
            const userLibraryDataList: Array<DocumentReference> = userLibraryQuerySnapshot.docs[0].get("book_ids");

            for (let i = 0; i < userLibraryDataList.length; i++) {
                const bookSnapshot: DocumentSnapshot = await getDoc(userLibraryDataList[i]);

                let book: Book = this.convertBookSnapshotToCommonFormat(bookSnapshot);
                library.push(book);
            }

            return library;
        }
        
        else {
            return "";
        }
    }

    private convertBookSnapshotToCommonFormat(bookSnapshot: DocumentSnapshot): Book {
        let commonFormatBoot: Book = {
            ISBN: bookSnapshot.get("ISBN"),
            authors: bookSnapshot.get("authors"),
            book_id: bookSnapshot.get("book_id"),
            cover_image: bookSnapshot.get("cover_image"),
            description: bookSnapshot.get("description"),
            genres: bookSnapshot.get("genres"),
            language: bookSnapshot.get("language"),
            page_count: bookSnapshot.get("page_count"),
            publication_date: bookSnapshot.get("publication_date"),
            publisher: bookSnapshot.get("publisher"),
            title: bookSnapshot.get("title")
        };

        return commonFormatBoot;
    }
}

export default LibraryDataClient;
