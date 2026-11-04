# on-exactitude-in-science
Map of the World

<img src="screenshot.png" />

## Quickstart

Fetch the Discogs dataset:

```
make fetch-dataset
```

Pull and build Docker images:

```
docker-compose pull
docker-compose build
```

Bring JanusGraph online and populate it:

```
make LIMIT=10000 load-from-scratch
```

Bring the API container online:

```
docker-compose up -d backend
```

Build the GUI:

```
make build-gui
```

Bring the GUI container online:

```
docker-compose up -d frontend
```

Now you can visit localhost:8080 to see.

## Debugging

Pull up a Gremlin console in Docker:

```
docker exec -it $(docker-compose ps --quiet janusgraph) ./bin/gremlin.sh
```

... or in Kubernetes:

```
kubectl exec -tic janusgraph $(kubectl get pods --selector=app=janusgraph -o jsonpath="{.items[0].metadata.name}") -- ./bin/gremlin.sh
```

... then run the following:

```
:remote connect tinkerpop.server conf/remote.yaml session
:remote console
```

```
job = graph.compute().program(PageRankVertexProgram.build().property("page_rank").create()).result(GraphComputer.ResultGraph.ORIGINAL).persist(GraphComputer.Persist.VERTEX_PROPERTIES).submit()
```
