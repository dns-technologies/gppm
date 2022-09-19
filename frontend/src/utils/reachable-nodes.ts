// Полезно: https://adelachao.medium.com/graph-topological-sort-javascript-implementation-1cc04e10f181

export class Graph {
    adjacencyList;

    constructor() {
        this.adjacencyList = new Object();
    }

    addVertex(vertex) {
        if (!this.adjacencyList[vertex]) {
            this.adjacencyList[vertex] = [];
        }
    }

    addEdge(v1, v2) {
        this.addVertex(v1);
        this.addVertex(v2);
        this.adjacencyList[v1].push(v2);
    }

    dfsTopSortHelper(v, visited, topNums) {
        visited.add(v);
        const neighbors = this.adjacencyList[v];
        for (const neighbor of neighbors) {
            if (!visited.has(neighbor)) {
                this.dfsTopSortHelper(neighbor, visited, topNums);
            }
        }
        topNums.push(v);
    }

    childsList() {
        return this.adjacencyList;
    }

    dfsTopSort() {
        const vertices = Object.keys(this.adjacencyList);
        const visited = new Set();
        let topNums = new Array();

        for (const v of vertices) {
            if (!visited.has(v)) {
                this.dfsTopSortHelper(v, visited, topNums);
            }
        }

        return topNums;
    }

    allReachableNodes() {
        const vertices = this.dfsTopSort();
        const dependencies = new Object();

        for (const v of vertices) {
            dependencies[v] = new Set();
            const neighbors = this.adjacencyList[v];
            for (const n of neighbors) {
                dependencies[v].add(n);
                dependencies[n].forEach(d => dependencies[v].add(d));
            }
            dependencies[v] = Array.from(dependencies[v]);
        }

        return dependencies;
    }
}
