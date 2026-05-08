import { useAuth0, withAuthenticationRequired } from "@auth0/auth0-react";
import { Trash2Icon } from "lucide-react";
import { useCallback, useEffect, useState } from "react";
import { Button } from "../ui/button";
import { Card, CardContent, CardDescription, CardFooter, CardTitle } from "../ui/card";

import { useAxiosInterceptor } from "@/hooks/use-axios-interceptor";
import type { Book } from "@/interfaces/Book";
import { apiService } from "@/services/bookworm-api";
import Header from "../header/header";

function Home() {
  useAxiosInterceptor();
  const [userLibrary, setUserBooks] = useState<Book[]>([]);
  const { isLoading, isAuthenticated } = useAuth0();

  const fetchUserLibrary = useCallback(() => {
    apiService.getUserBooks()
      .then(response => {
        setUserBooks(response.data);
      })
      .catch(error => {
        console.error(error);
      })
  }, []);

  const deleteUserBook = (userBookId: number) => {
    apiService.deleteUserBook(userBookId)
      .then(() => {
        fetchUserLibrary();
      })
      .catch(error => {
        console.error(error);
      })
  }

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      apiService.sendUserDataToServer()
        .catch(error => {
          console.error(error);
        })
    }
  }, [isLoading, isAuthenticated]);

  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      fetchUserLibrary();
    }
  }, [isLoading, isAuthenticated, fetchUserLibrary]);

  return (
    <>
      <Header onBookAdded={fetchUserLibrary} />
      <main className="flex flex-wrap">
        {userLibrary.length === 0
          ? <p className="p-5 text-muted-foreground"> (Your Library is empty) </p>
          : userLibrary.map(book => (
            <Card key={book.id} className="items-center max-w-40 min-h-60 m-5">
              <CardTitle>{book.title}</CardTitle>
              <CardDescription>By {book.author}</CardDescription>
              <CardContent>
                Status: {book.readingStatus}
              </CardContent>
              <CardFooter>{book.description}</CardFooter>
              <Button variant="outline" size="icon" onClick={() => deleteUserBook(book.id)}>
                <Trash2Icon />
              </Button>
            </Card>
          ))}
      </main>
    </>
  )
}

const ProtectedHome = withAuthenticationRequired(Home, {
  onRedirecting: () => <main>Redirecting to Login...</main>
});
export default ProtectedHome;
