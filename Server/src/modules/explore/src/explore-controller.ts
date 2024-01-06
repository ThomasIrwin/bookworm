import express, { Request, Response } from "express";
import ExploreService from "./explore-service";

let ExploreController = express.Router();
let explore_service = new ExploreService();

ExploreController.get("/", (req: Request, res: Response) => {
  let { query } = req;
  let { input } = query;
  let input_as_string: string | undefined = input?.toString();
  explore_service.getSearchResults(input_as_string);
});

export default ExploreController;
