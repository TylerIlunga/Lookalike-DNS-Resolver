1. The swarm size at which failures begin to manifest

- Failures began to manifest at 1050 users with a hatch size of 100 users spawned per second.

2. The maximum requests-per-second that your service was able to achieve

- The max was 6337.8 requests-per-second with 10000 users and a hatch size of 100 users spawned per second.

3. The swarm size at which the host reached capacity (i.e., “Too many open files”)

- The swarm size was 1000 users with a hatch size of 100 users spawned per second.

4. Commentary on any observed differences between the performance of your servers in this language as opposed to the previous one

- With Node.js being naturally single-threaded, I believe that could have been a core reason for its inferior performance. The failures were the same, however, the Node.js server experience the failures at 1050 users instead of 1400 users. Knowing spawning new threads and forking new process clearly has a performance tradeoff. Python required less code to develop both the client and server. Also, getting around Node.js's buffer concatenation ability was not so fun. In Python, one could just create a new Byte array and using the "+=" operator or the "append" method to concatenate more bytes. In Node.js, you have to create a completely new buffer, pass in an array of both the original buffer and the buffer with the bytes you would like to concatenate as an the first argument for "Buffer.from" and a second argument with the sum of both buffer's lengths.

5. Any other observations/behaviors that you find notable

- N/A
