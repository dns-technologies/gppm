# Helm Chart

This Helm chart allows you to deploy GreenPlum Permission Manager to Kubernetes cluster. You can install the chart by running the following command:

```
helm install gppm \
    -f values.yaml \
    -n gppm-prod \
    --generate-name
```

Have a look at the [values.yaml](./gppm/values.yaml) file to see the available options. 
