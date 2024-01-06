import express, { Request, Response } from "express";

import LibraryService from "./library-service";

let LibraryController = express.Router();
let lib_service = new LibraryService();

LibraryController.get("/:id", (req: Request, res: Response) => {
    console.log("lib controller");
    const { params } = req;
    const { id } = params;
    try {
        lib_service.getUserLibraryData(id)
            .then((response) => {
                if (response === "") {
                    // The document requested does not exist in the Database
                    res.status(400).json({ status: "error", message: "User Not Found" });
                }
                else {
                    // Found the document, return its contents
                    res.status(200).json(response);
                }
            });
    }
    catch(error: any) {
        res.json({ status: "error", message: error.message });
    }
});

export default LibraryController;
