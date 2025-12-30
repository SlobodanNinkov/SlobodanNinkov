---

layout: post
title: Docker Container Networking
subtitle: 
comments: true
mathjax: true
author: Slobodan Ninkov

---

Problem: In the docker system, when container is started it does not see other containers running on the same Docker. This problem comes up often during the testing and experimentation when you want to connect a python notebook with several databases. To make it happen, there are 2 steps you need to do.
  
# Step 1. Create local network in the docker  
`docker network create <network_name>`  

Example:  
`docker network create locnetwork`  

# Step 2. Add containers to the configured docker local network  
`docker network connect <network_name> <running_container>`  
  
Examples:  
`docker network connect locnetwork metabase`  
`docker network connect locnetwork postgres-interlinedlist`  

`locnetwork => name of the local network`  
`metabase => running container`  
`postgres-interlinedlist => running container`  


# Step 3. Read the IP-s from the docker network and configure python notebook and other containers with IP-s where they should send or query data.
`docker inspect <network_name>`  
`docker inspect locnetwork` => Show local network configuration, here you will find IP-s for each container.  

```json
{
 "Containers": {
            "4fc9fb3c919d720e9e07d819260e78d60f0c4d5461884d643a6541dd688b3875": {
                "Name": "postgres-interlinedlist",
                "EndpointID": "b9cdc787e44a3fb9290e69b7c6c18899e619066491c7c1185e0c4f0f7e9a6d70",
                "MacAddress": "5a:77:66:f7:72:41",
                "IPv4Address": "172.18.0.3/16",
                "IPv6Address": ""
            },
            "c4db0a1638e308b9a6ea7ddecde1ee46f664f85ccb0b73bc89adaa12f1be7853": {
                "Name": "metabase",
                "EndpointID": "83348dd668e1eb105075538cb119c8c5af7e9a91a2850897cda5e8b3ebeca720",
                "MacAddress": "e6:25:72:dc:31:67",
                "IPv4Address": "172.18.0.2/16",
                "IPv6Address": ""
            }
        }
}
```
