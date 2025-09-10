package com.bookworm.server.userbooks.enums;

public enum ReadingStatus {
    WANT_TO_READ("Want to Read"),
    CURRENTLY_READING("Currently Reading"),
    FINISHED("Finished"),
    PD("Put Down");
    
    private final String displayName;
    
    ReadingStatus(String displayName) {
        this.displayName = displayName;
    }
    
    public String getDisplayName() {
        return displayName;
    }
}
