import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogClose,
    DialogContent,
    DialogDescription,
    DialogFooter,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Field, FieldGroup, FieldLabel } from "@/components/ui/field";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

import type { AddBookRequest } from "@/interfaces/Book";
import { ReadingStatus } from "@/interfaces/ReadingStatus/ReadingStatus";
import { ReadingStatusDisplayName } from "@/interfaces/ReadingStatus/ReadingStatusDisplayName";
import { apiService } from "@/services/bookworm-api";

import { useState } from "react";

interface AddBookDialogProps {
    onBookAdded: () => void;
}

export default function AddBookDialog({ onBookAdded }: AddBookDialogProps) {
    const [title, setTitle] = useState<string>('');
    const [author, setAuthor] = useState<string>('');
    const [description, setDescription] = useState<string>('');
    const [readingStatus, setReadingStatus] = useState<ReadingStatus>(ReadingStatus.WANT_TO_READ);

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();

        const newBook: AddBookRequest = {
            title: title,
            author: author,
            description: description,
            readingStatus: readingStatus
        }

        console.log(newBook);
        apiService.addBookToUserLibrary(newBook)
            .then(response => {
                console.log(response.data);
                onBookAdded();
            })
            .catch(error => {
                console.error(error);
            })
    }

    return (
        <Dialog>
            <DialogTrigger asChild>
                <Button className='mr-[20px]' variant="outline">Add Book</Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-sm">
                <form onSubmit={handleSubmit}>
                    <DialogHeader>
                        <DialogTitle>Add Book</DialogTitle>
                        <DialogDescription>
                            Fill in the details of the book you'd like to add. Click Save when you're done.
                        </DialogDescription>
                    </DialogHeader>
                    <FieldGroup className="mt-5">
                        <Field>
                            <Label htmlFor="form-title">Title</Label>
                            <Input
                                id="form-title"
                                name="title"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                placeholder='1984' />
                        </Field>
                        <Field>
                            <Label htmlFor="form-author">Author</Label>
                            <Input
                                id="form-author"
                                name="author"
                                value={author}
                                onChange={(e) => setAuthor(e.target.value)}
                                placeholder='George Orwell' />
                        </Field>
                        <Field>
                            <Label htmlFor="form-description">Description</Label>
                            <Input
                                id="form-description"
                                name="description"
                                value={description}
                                onChange={(e) => setDescription(e.target.value)}
                                placeholder='one of the most significant novels of world literature and for sure one of the most famous
                                dystopian novels of all times. It speaks of the totalitarian system that rules in the future (considering
                                the time the novel was written) and about a single person trying to survive.' />
                        </Field>
                        <Field>
                            <FieldLabel htmlFor="form-reading-status">Reading Status</FieldLabel>
                            <Select
                                value={readingStatus}
                                onValueChange={(value) => setReadingStatus(value as ReadingStatus)}
                            >
                                <SelectTrigger id="form-reading-status">
                                    <SelectValue placeholder="Select a status" />
                                </SelectTrigger>
                                <SelectContent>
                                    <SelectGroup>
                                        {Object.values(ReadingStatus).map((status) => (
                                            <SelectItem key={status} value={status}>
                                                {ReadingStatusDisplayName[status]}
                                            </SelectItem>
                                        ))}
                                    </SelectGroup>
                                </SelectContent>
                            </Select>
                        </Field>
                    </FieldGroup>
                    <DialogFooter className="mt-5">
                        <DialogClose asChild>
                            <Button type="submit">Save</Button>
                        </DialogClose>
                        <DialogClose asChild>
                            <Button variant="outline">Cancel</Button>
                        </DialogClose>
                    </DialogFooter>
                </form>
            </DialogContent>
        </Dialog>
    )
}