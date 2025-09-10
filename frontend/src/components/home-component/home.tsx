import { useAuth0, withAuthenticationRequired } from "@auth0/auth0-react";
import { useEffect, useState } from "react";
import { Card, CardFooter, CardTitle } from "../ui/card";

import type { Book } from "@/interfaces/Book";
import { apiService } from "@/services/bookworm-api";
import Header from "../header/header";

function Home() {
  const [userLibrary, setUserLibrary] = useState<Book[]>([]);
  const { user, isLoading } = useAuth0();

  const sendUserDataToServer = () => {
    apiService.sendUserDataToServer(user?.sub!, user?.email!)
      .then(response => {
        console.log("Success: ", response.data);
      })
      .catch(error => {
        console.error(error);
      })
  }

  useEffect(() => {
    if (user?.sub && user?.email) {
      sendUserDataToServer();
    }
  }, [isLoading, user?.sub, user?.email]);

  useEffect(() => {
    apiService.getUserLibrary(user?.sub!)
      .then(response => {
        console.log(response.data);
        // PCK UP HERE, NEED TO RE-MAP THE DATA CORRECTLY
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
  }, [isLoading, user?.sub]);

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