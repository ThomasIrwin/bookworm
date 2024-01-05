import { NgIf } from '@angular/common';
import { Component } from '@angular/core';
import { FormControl, ReactiveFormsModule, Validators } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatIconModule } from '@angular/material/icon';
import { MatInputModule } from '@angular/material/input';

@Component({
  selector: 'app-explore',
  templateUrl: './explore.component.html',
  styleUrls: ['./explore.component.scss'],
  standalone: true,
  imports: [MatFormFieldModule, MatInputModule, MatIconModule, ReactiveFormsModule, NgIf]
})
export class ExploreComponent {


  explore_searchbar_user_input = new FormControl('', [
    Validators.maxLength(64),
  ]);

  getSearchErrorMessage() {
    return this.explore_searchbar_user_input.hasError("maxLength") ? "Your Search is Too Long" : "";
  }

  handleSearchClick(explore_searchbar_user_input: FormControl) {
    if (explore_searchbar_user_input.valid) {
      const input_as_string: string = explore_searchbar_user_input.value;
      console.log(input_as_string);
    }
    console.log("User input is invalid (probably too long)");
  }
}
