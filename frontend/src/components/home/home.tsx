import { useAuth0, withAuthenticationRequired } from "@auth0/auth0-react";
import { useEffect, useState } from "react";
import { Card, CardContent, CardDescription, CardFooter, CardTitle } from "../ui/card";

import { useAxiosInterceptor } from "@/hooks/use-axios-interceptor";
import type { Book } from "@/interfaces/Book";
import { apiService } from "@/services/bookworm-api";
import Header from "../header/header";

function Home() {
  useAxiosInterceptor();
  const [userLibrary, setUserBooks] = useState<Book[]>([]);
  const { isLoading } = useAuth0();

  const fetchUserLibrary = () => {
    apiService.getUserBooks()
      .then(response => {
        console.log(response.data);
        setUserBooks(response.data);
      })
      .catch(error => {
        console.error(error);
      })
  };

  useEffect(() => {
    apiService.sendUserDataToServer()
      .then(response => {
        console.log("User Logged In", response.data);
      })
      .catch(error => {
        console.error(error);
      })
  }, [isLoading]);

  useEffect(() => {
    fetchUserLibrary();
  }, [isLoading]);

  return (
    <>
      <Header onBookAdded={fetchUserLibrary} />
      <main className="flex flex-wrap">
        {userLibrary.map(book => (
          <Card key={book.id} className="items-center max-w-40 min-h-60 m-5">
            <CardTitle>{book.title}</CardTitle>
            <CardDescription>By {book.author}</CardDescription>
            <CardContent>
              Status: {book.readingStatus}
            </CardContent>
            <CardFooter>{book.description}</CardFooter>
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
