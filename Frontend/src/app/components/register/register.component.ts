import { Component, OnInit, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormControl, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';

import { NgIf } from '@angular/common';

import { Router } from '@angular/router';

import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-register',
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.scss'],
  standalone: true,
  imports: [
    MatCardModule,
    MatFormFieldModule,
    MatInputModule,
    ReactiveFormsModule,
    MatButtonModule,
    NgIf,
  ],
})
export class RegisterComponent {
  private auth = inject(AuthService);
  private router = inject(Router);

  email = new FormControl('', [
    Validators.email,
    Validators.required,
    Validators.minLength(5),
  ]);

  username = new FormControl('', [
    Validators.required,
    Validators.minLength(5),
  ]);

  password = new FormControl('', [
    Validators.required,
    Validators.minLength(10),
  ]);

  getEmailErrorMessage() {
    if (this.email.hasError('required')) {
      return 'You must enter a value';
    }

    return this.email.hasError('email') ? 'Not a valid email' : '';
  }

  getUsernameErrorMessage() {
    if (this.username.hasError('required')) {
      return 'You must enter a value';
    }

    return this.username.hasError('username') ? 'Not a valid username' : '';
  }

  getPasswordErrorMessage() {
    if (this.password.hasError('required')) {
      return 'You must enter a value';
    }

    return this.password.hasError('minlength') ? 'Password Too Short' : '';
  }

  handleRegistrationClick(
    email: FormControl,
    username: FormControl,
    password: FormControl
  ) {
    if (email.valid && username.valid && password.valid) {
      const email_as_string: string = email.value;
      const username_as_string: string = username.value;
      const password_as_string: string = password.value;

      this.auth.register(
        email_as_string,
        username_as_string,
        password_as_string
      );
    } else {
      console.log('email, username, or password is invalid');
    }
  }

  redirectToLogin() {
    this.router.navigate(['login']);
  }
}
