import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';

import {
  Auth,
  signOut,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  UserCredential,
} from '@angular/fire/auth';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private router = inject(Router);
  private auth = inject(Auth);

  private user: any = {};

  login(email: string, password: string) {
    signInWithEmailAndPassword(this.auth, email, password)
      .then((result) => {
        this.user = result.user;
        this.router.navigate(['home']);
      })
      .catch((err) => {
        console.log('Something went wrong: ', err.message);
      });
  }

  register(email: string, password: string) {
    createUserWithEmailAndPassword(this.auth, email, password)
      .then((result) => {
        this.user = result.user;
        this.router.navigate(['home']);
      })
      .catch((err) => {
        console.log('Something went wrong: ', err.message);
      });
  }

  getUser(): UserCredential {
    return this.user;
  }

  logout() {
    signOut(this.auth);
    this.user = {};
    this.router.navigate(['']);
  }
}
