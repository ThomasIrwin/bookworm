import express, { Request, Response } from "express";
import ExploreDataClient from "./explore-data-access";
import ExploreService from "./explore-service";

let ExploreController = express.Router();

let explore_data_client = new ExploreDataClient();
let explore_service = new ExploreService(explore_data_client);

ExploreController.get("/", (req: Request, res: Response) => {
  let { query } = req;
  let { input } = query;
  let input_as_string: string | undefined = input?.toString();
  try {
    explore_service.getSearchResults(input_as_string)
      .then((response) => {
        if (response === "") {
          res.status(400).json({ status: "error", message: "Search Unsuccessful" })
        }
        else {
          res.status(200).json(response);
        }
      });
  }
  catch (error: any) {
    res.json({ status: "error", message: error.message });
  }
});

export default ExploreController;
