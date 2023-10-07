import express, { Express } from "express";
import cors from 'cors';
import bodyParser from "body-parser";
import helmet from "helmet";
import dotenv from "dotenv";

import indexRouter from "./routes/routes";

dotenv.config();

const PORT = process.env.port || 8080;

const app: Express = express();

app.use(helmet());
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

app.use("/api/v1", indexRouter);

app.listen(PORT, () => console.log(`Running on port ${PORT}`));
