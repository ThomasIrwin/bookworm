import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';

import {
  Auth,
  signOut,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
} from '@angular/fire/auth';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private router = inject(Router);
  private auth = inject(Auth);

  login(email: string, password: string) {
    signInWithEmailAndPassword(this.auth, email, password)
      .then((user) => {
        this.router.navigate(['home']);
      })
      .catch((err) => {
        console.log('Something went wrong: ', err.message);
      });
  }

  register(email: string, password: string) {
    createUserWithEmailAndPassword(this.auth, email, password)
      .then((user) => {
        this.router.navigate(['home']);
      })
      .catch((err) => {
        console.log('Something went wrong: ', err.message);
      });
  }

  logout() {
    signOut(this.auth);
    this.router.navigate(['']);
  }
}
