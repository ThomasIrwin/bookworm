import { Injectable, inject } from '@angular/core';
import { Router } from '@angular/router';

import {
  Auth,
  updateProfile,
  signOut,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  UserCredential,
  User,
} from '@angular/fire/auth';

import { doc, setDoc, Firestore } from '@angular/fire/firestore';

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private router: Router = inject(Router);
  private auth: Auth = inject(Auth);
  private firestore_db: Firestore = inject(Firestore);

  login(email: string, password: string) {
    signInWithEmailAndPassword(this.auth, email, password)
      .then(() => {
        this.router.navigate(['home']);
      })
      .catch((err) => {
        console.log('Something went wrong: ', err.message);
      });
  }

  register(email: string, username: string, password: string) {
    createUserWithEmailAndPassword(this.auth, email, password)
      .then((user_credentials) => {
        updateProfile(user_credentials.user, {
          displayName: username,
        }).then(() => {
          setDoc(
            doc(this.firestore_db, 'users', `${user_credentials.user.uid}`),
            {
              email: user_credentials.user.email,
              uid: user_credentials.user.uid,
              username: this.auth.currentUser?.displayName,
            }
          );
          this.router.navigate(['home']);
        });
      })
      .catch((err) => {
        console.log('Something went wrong: ', err.message);
      });
  }

  getUser(): User | null {
    return this.auth.currentUser;
  }

  getUserId(): string {
    if (this.isLoggedIn()) {
      return this.auth.currentUser?.uid!;
    } else {
      return '';
    }
  }

  getUsername(): string {
    if (this.isLoggedIn()) {
      return this.auth.currentUser?.displayName!;
    } else {
      return '';
    }
  }

  isLoggedIn(): boolean {
    return this.auth.currentUser !== null;
  }

  logout() {
    signOut(this.auth);
    this.router.navigate(['']);
  }
}
