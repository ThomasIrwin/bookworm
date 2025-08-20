import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardTitle } from "../ui/card";

import Header from "../header/header"
import { apiService } from "@/services/bookworm-api";
import type { Book } from "@/interfaces/Book";

export default function Home() {
  const [userLibrary, setUserLibrary] = useState<Book[]>([]);

  useEffect( () => {
    apiService.getUserLibrary()
      .then( response => {
        let user_library_data: Book[] =
          response.data.map( (raw_book_data: any) => ({
            id: raw_book_data.id,
            title: raw_book_data.title,
            author: raw_book_data.author,
            description: raw_book_data.description,
          }))
        setUserLibrary(user_library_data);
      })
      .catch (error => {
        console.error("Error: ", error);
      })
  }, []);

  return (
    <>
      <Header />
      { userLibrary.map( book => (
        <Card key={ book.id } className="items-center max-w-50 m-5">
          <CardTitle>{ book.title }</CardTitle>
          <CardDescription>By { book.author }</CardDescription>
          <CardContent>
            <p>{ book.description }</p>
          </CardContent>
        </Card>
      ))}
    </>
  )
}