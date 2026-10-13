import * as dotenv from "dotenv";
import { createPool } from "mysql2/promise";

dotenv.config();

for (const key of [
  "MYSQL_HOST",
  "MYSQL_USER",
  "MYSQL_PASSWORD",
  "MYSQL_DATABASE",
]) {
  if (!process.env[key]) {
    throw new Error(`Missing setting: ${key}`);
  }
}

export const pool = createPool({
  host: process.env.MYSQL_HOST,
  port: Number(process.env.MYSQL_PORT ?? 3306),
  user: process.env.MYSQL_USER,
  password: process.env.MYSQL_PASSWORD,
  database: process.env.MYSQL_DATABASE,
  waitForConnections: true,
  connectionLimit: 5,
  connectTimeout: 10000,
});