# homework
the modflow homework repository

## Installation of modflow image

Navigate to the homework-folder

```shell
docker build -t inowas/modflow .
```

For the installation you will need a internet connection and some time.

## Run the modflow example

```shell
docker run -t -v $(pwd)/data:/data inowas/modflow python lake_example.py
```
