import express from "express";

import LibraryController from "../modules/library/src/library-controller";

let indexRouter = express.Router();

indexRouter.use("/library", LibraryController);

export default indexRouter;