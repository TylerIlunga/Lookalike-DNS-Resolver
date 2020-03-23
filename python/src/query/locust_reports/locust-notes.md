1. The swarm size at which failures begin to manifest

- Failures began to manifest at 1400 users with a hatch size of 100 users spawned per second.

2. The maximum requests-per-second that your service was able to achieve

- The max was 6501.9 requests-per-second with 10000 users and a hatch size of 100 users spawned per second.

3. The swarm size at which the host reached capacity (i.e., “Too many open files”)

- The swarm size was 1400 users with a hatch size of 100 users spawned per second.

4. Any other observations/behaviors that you find notable

- I encountered a similar error while testing this server as well. I received more "gaierror" messages while testing. It stems from the OSError where memory no longer can be allocated for a open file, thus a socket cannot be created, and therefore leading to issues for the SocketUser class and the SocketUser's host value not being properly set. Also, again, even though the server hit failures at 1400 users, at 1500 users/100 spawned per second there were no failures at all!
