import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Menu } from 'lucide-react';
import { Link } from 'react-router-dom';

import LogoutButton from "./logout-button";

import { Input } from "@/components/ui/input";
import AddBookDialog from './add-book-dialog';

interface HeaderProps {
  onBookAdded: () => void;
}

export default function Header({ onBookAdded }: HeaderProps) {

  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="flex h-14 items-center mr-[20px]">
        {/* Mobile menu button - only visible on mobile */}
        <button className="inline-flex items-center justify-center rounded-md p-2 text-sm font-medium ring-offset-background transition-colors hover:bg-accent hover:text-accent-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50 md:hidden">
          <Menu className="h-5 w-5" />
          <span className="sr-only">Toggle menu</span>
        </button>

        {/* Logo/Brand */}
        <div className="mr-4 hidden md:flex">
          <Link className="mr-6 flex items-center space-x-2" to="/home">
            <span className="hidden font-bold text-[30px] sm:inline-block ml-2"> Bookworm </span>
          </Link>
        </div>

        <Tabs defaultValue="library" className="w-[400px]">
          <TabsList>
            <TabsTrigger value="home">Home</TabsTrigger>
            <TabsTrigger value="library">Library</TabsTrigger>
            <TabsTrigger value="stats">Stats</TabsTrigger>
            <TabsTrigger value="plan">Plan</TabsTrigger>
            <TabsTrigger value="friends">Friends</TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Search Bar */}
        <Input className='ml-[2rem] mr-[20rem] max-w-lg' placeholder='Search...' />
        <AddBookDialog onBookAdded={onBookAdded} />
        <LogoutButton />
      </div>
    </header>
  );
}