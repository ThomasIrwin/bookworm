class LibraryDataClient {
    constructor() {}

    getUserLibraryData(user_id: string) {
        const library = [
            {
                title: "1984",
                author: "George Orwell",
                pages: 281
            }
        ];
        console.log('user id: ' + user_id + '. Library: ' + library);
        return library;
    }
}

export default LibraryDataClient;