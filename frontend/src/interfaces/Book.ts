
export interface AddBookRequest {
    title: string;
    author: string;
    description: string;
    readingStatus: string;
}

export interface Book {
    id: number;
    title: string;
    author: string;
    description: string;
    readingStatus: string;
}