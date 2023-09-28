import { Component, inject } from '@angular/core';

import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';

import { AuthService } from 'src/app/services/auth.service';

import { LibraryComponent } from '../library/library.component';

enum TAB_SELECTION {
  LIBRARY = 1,
  EXPLORE = 2,
  PROFILE = 3,
  READING_PLAN = 4,
}

@Component({
  selector: 'app-home',
  templateUrl: './home.component.html',
  styleUrls: ['./home.component.scss'],
  standalone: true,
  imports: [
    LibraryComponent,
    MatSidenavModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatDividerModule,
  ],
})
export class HomeComponent {
  private auth = inject(AuthService);

  navigateToLibrary() {}

  navigateToExplore() {}

  navigateToProfile() {}

  navigateToReadingPlan() {}

  handleLogout() {
    this.auth.logout();
  }
}
