# Counting unique colors on Nasa's POD.

[![CI](https://github.com/alejandro-zuleta-globant/nasa-pod/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/alejandro-zuleta-globant/nasa-pod/actions/workflows/python-app.yml)

This is small project for counting the unique colors from the Nasa's Picture of the Day. The data is got via Nasa's API so you will require an authorized API KEY. You can use this CLI by running the following commands, passing the _mode_ argument and the options _start date_ and _end_date_:

```shell
python main.py sync --start_date 2022-01-13 --end_date 2022-01-15
```

Four modes are supported:

- `sync`: Sequentially gets a picture for each day in the given period.
- `async`: Gets the pictures in an asynchronous process, using aiohttp and async/await constructs.
- `threading`: Spawns multiple threads to get the pictures for each day.
- `multiprocessing`: Generates a pool of processes to get the pictures for each day.

This project is just a test aimed to evaluate different approaches for I/O related use cases.

Before running the script, export a environment variable set to the API URL including your API key as query string:

```shell
export API_URL=https://api.nasa.gov/planetary/apod?api_key=YOUR_API_KEY
```
