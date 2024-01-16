import { Component, Input, OnInit } from '@angular/core';
import { MatDialog, MatDialogModule } from '@angular/material/dialog';
import { Book } from '../../../../../DataModel/Book';
import { BookDialogComponent } from "../book-dialog/book-dialog.component";

@Component({
  selector: 'app-book-display',
  templateUrl: './book-display.component.html',
  styleUrls: ['./book-display.component.scss'],
  standalone: true,
  imports: [ MatDialogModule ]
})
export class BookDisplayComponent implements OnInit {
  @Input({ required: true }) book_data: Book;

  constructor(public dialog: MatDialog) {}

  openQuickBookLookDialog() {
    let dialogRef = this.dialog.open(BookDialogComponent, {
      width: "350px",
      data: this.book_data
    });

    dialogRef.afterClosed().subscribe(result => {
      console.log(result);
    })
  }

  ngOnInit(): void {
      
  }

}
