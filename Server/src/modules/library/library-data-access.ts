class LibraryDataClient {
    constructor() {}

    getUserLibraryData(user_id: string) {
        console.log("user ID: " + user_id);
        return {
            status: "Success",
            libraryData: {
                user: "Cornelius Plumbottom",
                books: [
                    {
                        title: "1984",
                        author: "George Orwell",
                        pages: 281
                    }
                ]
            }
        };
    }
}

export default LibraryDataClient;