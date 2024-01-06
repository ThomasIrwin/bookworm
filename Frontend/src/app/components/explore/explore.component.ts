import { NgIf } from '@angular/common';
import { Component, inject } from '@angular/core';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';
import { Observable } from 'rxjs';

import { ExploreService } from 'src/app/services/explore.service';
import { Book } from '../../../../../DataModel/Book';

@Component({
  selector: 'app-explore',
  templateUrl: './explore.component.html',
  styleUrls: ['./explore.component.scss'],
  standalone: true,
  imports: [MatFormFieldModule, MatInputModule, MatIconModule, ReactiveFormsModule, NgIf]
})
export class ExploreComponent {
  private _explore_service = inject(ExploreService);

  search_results: Observable<Book[]> | undefined;

  explore_searchbar_user_input = new FormControl('', [
    Validators.maxLength(64),
  ]);

  getSearchErrorMessage() {
    return this.explore_searchbar_user_input.hasError("maxlength") ? "Your Search is Too Long" : "";
  }

  handleSearchClick(explore_searchbar_user_input: FormControl) {
    if (explore_searchbar_user_input.valid) {
      const input_as_string: string = explore_searchbar_user_input.value;
      if (input_as_string !== "" || input_as_string === undefined) {
        this._explore_service.getSearchResults(input_as_string)
        .subscribe((result) => {
          console.log(result);
        })
      } else {
        console.log("Empty or undefined search query");
      }
    } else {
      console.log("User input is invalid (probably too long)");
    }
  }
}
