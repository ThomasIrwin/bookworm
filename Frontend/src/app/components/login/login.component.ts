import { Component, OnInit, inject } from '@angular/core';
import { MatCardModule } from '@angular/material/card';
import { MatInputModule } from '@angular/material/input';
import { MatFormFieldModule } from '@angular/material/form-field';
import { FormControl, Validators, ReactiveFormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';

import { Router } from '@angular/router';

import { NgIf } from '@angular/common';

import { AuthService } from 'src/app/services/auth.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
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
export class LoginComponent implements OnInit {
  private auth = inject(AuthService);
  private router = inject(Router);

  email = new FormControl('', [
    Validators.email,
    Validators.required,
    Validators.minLength(5),
  ]);

  password = new FormControl('', [
    Validators.required,
    Validators.minLength(10),
  ]);

  ngOnInit() {}

  getEmailErrorMessage() {
    if (this.email.hasError('required')) {
      return 'You must enter a value';
    }

    return this.email.hasError('email') ? 'Not a valid email' : '';
  }

  getPasswordErrorMessage() {
    if (this.password.hasError('required')) {
      return 'You must enter a value';
    }

    return this.password.hasError('minlength') ? 'Password Too Short' : '';
  }

  handleLoginClick(email: FormControl, password: FormControl) {
    if (email.valid && password.valid) {
      const email_as_string: string = email.value;
      const password_as_string: string = password.value;
      this.auth.login(email_as_string, password_as_string);
      email.reset;
      password.reset;
    } else {
      console.log('email or password is invalid');
    }
  }

  redirectToRegistration() {
    this.router.navigate(['register']);
  }
}
