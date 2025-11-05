import axios from "axios";
import express from "express";
import os from "os";
import cluster from "cluster";

const numCPUs = os.cpus().length;

if (cluster.isPrimary) {
    console.log(`Primary ${process.pid} is running`);

    // Fork workers.
    for (let i = 0; i < numCPUs; i++) {
        cluster.fork();
    }

    cluster.on("exit", (worker, code, signal) => {
        console.log(`worker ${worker.process.pid} died`);
    });
} else {
    console.log(`Worker ${process.pid} started`);
    startServer();
}

function startServer() {
    const PORT = process.env.PORT || 8080;
    const app = bootstrap();
    app.listen(PORT, () => {
        console.log(`started at ${PORT}`);
        console.log(`app url ${process.env.APP_URL}`);
    });
}

function bootstrap() {
    const app = express();

    // ---------------------------- ENTRY POINT
    app.get("/", (req, res) => {
        res.json({
            message: "Welcome to the performance test service",
            endpoints: [
                { method: "GET", path: "/fibonacci/:n" },
                { method: "GET", path: "/bubble-sort?n=<number>" },
            ],
        });
    });

    // ---------------------------- FIBONACCI
    const service = axios.create({ baseURL: process.env.APP_URL });

    app.get("/fibonacci/:n", async (req, res) => {
        const n = +req.params.n;
        const start = new Date();

        if (n == 1 || n == 2) {
            res.json({ fibonacci: 1, start: start, end: new Date() });
            return;
        }

        const nMinusOneRequest = service.get(`/fibonacci/${n - 1}`);
        const nMinusTwoRequest = service.get(`/fibonacci/${n - 2}`);

        const fibonacci =
            (await nMinusOneRequest).data.fibonacci +
            (await nMinusTwoRequest).data.fibonacci;

        res.json({
            start: start,
            fibonacci,
            end: new Date(),
        });

        return;
    });

    // ---------------------------- BUBBLE SORT
    app.get("/bubble-sort", (req, res) => {
        const n = +req.query.n;

        const arr = [];

        const start = new Date();

        for (let i = n; i > 0; i--) {
            arr.push(i);
        }

        bubbleSort(arr);

        const end = new Date();

        res.json({ start: start, end: end });
    });

    /**
     *
     * @param {number[]} arr
     */
    function bubbleSort(arr) {
        for (let i = arr.length; i > 0; i--)
            for (let j = 1; j < i; j++)
                if (arr[j] < arr[j - 1]) {
                    const swap = arr[j];
                    arr[j] = arr[j - 1];
                    arr[j - 1] = swap;
                }
    }

    return app;
}
