1. The swarm size at which failures begin to manifest

- Failures began to manifest at 1500 users with a hatch size of 100 users spawned per second.

2. The maximum requests-per-second that your service was able to achieve

- The max was 6515.9 requests-per-second with 10000 users and a hatch size of 100 users spawned per second.

3. The swarm size at which the host reached capacity (i.e., “Too many open files”)

- The swarm size was 1500 users with a hatch size of 100 users spawned per second.

4. Any other observations/behaviors that you find notable

- Besides the OSError, I received a "gaierror" as well. After doing some quick research, I discovered that the error code '8', indicating that "nodename nor servname provided, or not known", stems from the value set as "host" within the SocketUser class not being properly set. This likely stems the OSError where memory no longer can be allocated for an open file, thus a socket cannot be created, therefore leading to issues for the SocketUser class and the host value not being properly set. Also, even though the server hit failures at 1500 users, at 2000 users/100 spawned per second there were no failures at all!
