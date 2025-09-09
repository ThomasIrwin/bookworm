import { useAuth0, withAuthenticationRequired } from "@auth0/auth0-react";
import { useEffect, useState } from "react";
import { Card, CardFooter, CardTitle } from "../ui/card";

import type { Book } from "@/interfaces/Book";
import { apiService } from "@/services/bookworm-api";
import Header from "../header/header";

function Home() {
  const [userLibrary, setUserLibrary] = useState<Book[]>([]);
  const { user, getAccessTokenSilently } = useAuth0();

  const sendUserDataToServer = async () => {
    try {
      const token = await getAccessTokenSilently();
      apiService.sendUserDataToServer(token)
        .then(response => {
          console.log("Success: ", response.data);
        })
        .catch(error => {
          console.error(error);
        })
    } catch (error) {
      console.error("Error: ", error);
    }
  }
  sendUserDataToServer();

  useEffect(() => {
    apiService.getUserLibrary()
      .then(response => {
        const user_library_data: Book[] =
          response.data.map((raw_book_data: any) => ({
            id: raw_book_data.id,
            title: raw_book_data.title,
            author: raw_book_data.author,
            description: raw_book_data.description,
          }))
        setUserLibrary(user_library_data);
      })
      .catch(error => {
        console.error("Error: ", error);
      })
  }, []);

  return (
    <>
      <Header />
      <main className="flex flex-wrap">
        {userLibrary.map(book => (
          <Card key={book.id} className="items-center max-w-40 min-h-60 m-5">
            <CardTitle>{book.title}</CardTitle>
            <CardFooter>By {book.author}</CardFooter>
          </Card>
        ))}
      </main>
    </>
  )
}

export default withAuthenticationRequired(Home, {
  onRedirecting: () => <main> Redirecting to Login... </main>
})