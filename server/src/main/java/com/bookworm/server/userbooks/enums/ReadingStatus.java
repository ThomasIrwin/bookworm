package com.bookworm.server.userbooks.enums;

public enum ReadingStatus {
    WANT_TO_READ("Want to Read"),
    IN_PROGRESS("In Progress"),
    FINISHED("Finished"),
    PUT_DOWN("Put Down");

    private final String displayName;

    ReadingStatus(String displayName) {
        this.displayName = displayName;
    }

    public String getDisplayName() {
        return displayName;
    }
}
