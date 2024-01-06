import { Component, inject } from '@angular/core';

import { NgIf } from '@angular/common';

import { MatButtonModule } from '@angular/material/button';
import { MatDividerModule } from '@angular/material/divider';
import { MatIconModule } from '@angular/material/icon';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';

import { AuthService } from 'src/app/services/auth.service';

import { ExploreComponent } from '../explore/explore.component';
import { LibraryComponent } from '../library/library.component';
import { ProfileComponent } from '../profile/profile.component';
import { ReadingPlanComponent } from '../reading-plan/reading-plan.component';

enum TabSelection {
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
    ExploreComponent,
    ProfileComponent,
    ReadingPlanComponent,
    MatSidenavModule,
    MatToolbarModule,
    MatIconModule,
    MatButtonModule,
    MatDividerModule,
    NgIf,
  ],
})
export class HomeComponent {
  private _auth = inject(AuthService);
  public tab = TabSelection;
  private selected_tab = this.tab.LIBRARY;

  navigateToLibrary() {
    this.selected_tab = this.tab.LIBRARY;
  }

  navigateToExplore() {
    this.selected_tab = this.tab.EXPLORE;
  }

  navigateToProfile() {
    this.selected_tab = this.tab.PROFILE;
  }

  navigateToReadingPlan() {
    this.selected_tab = this.tab.READING_PLAN;
  }

  getCurrentTab() {
    return this.selected_tab;
  }

  getUsername() {
    return this._auth.getUsername();
  }

  handleLogout() {
    this._auth.logout();
  }
}
