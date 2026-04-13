export const ReadingStatus = {
    WANT_TO_READ: "WANT_TO_READ",
    IN_PROGRESS: "IN_PROGRESS",
    FINISHED: "FINISHED",
    PUT_DOWN: "PUT_DOWN"
} as const;

export type ReadingStatus = typeof ReadingStatus[keyof typeof ReadingStatus];