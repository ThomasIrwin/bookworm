import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { Book } from '../../../../../DataModel/Book';

@Component({
  selector: 'app-book-dialog',
  templateUrl: './book-dialog.component.html',
  styleUrls: ['./book-dialog.component.scss'],
  standalone: true
})
export class BookDialogComponent {
  constructor(public dialogRef: MatDialogRef<BookDialogComponent>, @Inject(MAT_DIALOG_DATA) public book_data: Book) { }

  onCancel() {
    this.dialogRef.close();
  }

  onConfirm() {
    this.dialogRef.close(this.book_data);
  }
}
