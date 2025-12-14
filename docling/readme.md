# Simple


## Prepear

```
cd docling/simple

docker build -t docling-simple .
```

## Run

cpu:
```
docker run --rm -v ${PWD}:/develop --name docling-simple docling-simple python simple_call.py
```

gpu:
```
docker run --rm --gpus all -v ${PWD}:/develop --name docling-simple docling-simple python simple_call.py
docker run --rm --gpus all -v ${PWD}:/develop --name docling-simple docling-simple python vlm_call.py
```

cd E:\document_parsing\docling\simple; docker run --rm -v ${PWD}:/develop --name docling-simple docling-simple python simple_call.py





# Serve


## Prepear


## Serve


## Test
