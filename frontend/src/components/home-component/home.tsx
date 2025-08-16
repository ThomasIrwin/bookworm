import { useEffect, useState } from "react";
import Header from "../header/header"
import { apiService } from "@/services/bookworm-api";

export default function Home() {
  const [userLibrary, setUserLibrary] = useState<string>("");

  useEffect( () => {
    apiService.getUserLibrary()
      .then( response => {
        setUserLibrary(prevLib => prevLib = response.data)
      })
      .catch (error => {
        console.error("Error: ", error);
      })
  }, []);

  return (
    <>
      <Header />
      <h1>{ userLibrary }</h1>
    </>
  )
}