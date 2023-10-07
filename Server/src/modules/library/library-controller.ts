import express, { Request, Response } from "express";

import LibraryService from "./library-service";

let LibraryController = express.Router();
let lib_service = new LibraryService();

LibraryController.get("/:id", (req: Request, res: Response) => {
    console.log('incoming request');
    const { params } = req;
    const { id } = params;
    try {
        const payload = lib_service.getUserLibraryData(id);
        res.json(payload);
    }
    catch(error: any) {
        res.json({ status: 'error', message: error.message });
    }
});

export default LibraryController;
