1. The swarm size at which failures begin to manifest

- Failures began to manifest at 1000 users with a hatch size of 100 users spawned per second.

2. The maximum requests-per-second that your service was able to achieve

- The max was 6501.8 requests-per-second with 10000 users and a hatch size of 100 users spawned per second.

3. The swarm size at which the host reached capacity (i.e., “Too many open files”)

- The swarm size was 1000 users with a hatch size of 100 users spawned per second.

4. Commentary on any observed differences between the performance of your servers in this language as opposed to the previous one

- Adding on top of the observed differences from the query server report, the Python server was able to attain a slightly higher rps value than the Node server. Additionally, byte arrays in Python allow you to simply slice the list via braces("[start:end]") while in Node you have to use the "subarray" method applied to all Buffers. Both behaviors set the end index as exclusive.

5. Any other observations/behaviors that you find notable

- I encountered a similar error that I experience while testing the python inverse query server. I received more "gaierror" messages while testing. It stems from the OSError where memory no longer can be allocated for a open file, thus a socket cannot be created, and therefore leading to issues for the SocketUser class and the SocketUser's host value not being properly set. Also, again, even though the server hit failures at 1000 users, at 1100 users/100 spawned per second there were no failures at all!
