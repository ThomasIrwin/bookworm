package com.bookworm.server.users.dto;

public class UserRequest {
    private String auth0Id;
    private String email;
    
    // constructors, getters, setters
    public UserRequest() {}
    
    public String getAuth0Id() { return auth0Id; }
    public void setAuth0Id(String auth0Id) { this.auth0Id = auth0Id; }
    
    public String getEmail() { return email; }
    public void setEmail(String email) { this.email = email; }
}