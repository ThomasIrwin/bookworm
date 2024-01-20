export interface Book {
    ISBN: string;
    authors: Array<string>;
    book_id: string;
    cover_image: string;
    description: string;
    genres: Array<string>;
    language: string;
    page_count: number;
    publication_date: Date;
    publisher: string;
    title: string;
}
