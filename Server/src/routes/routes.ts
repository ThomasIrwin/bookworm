import express from "express";

import ExploreController from "../modules/explore/src/explore-controller";
import LibraryController from "../modules/library/src/library-controller";

let indexRouter = express.Router();

indexRouter.use("/library", LibraryController);
indexRouter.use("/explore", ExploreController);

export default indexRouter;