/* 
    Client for One-Shot DNS Server using Inverse DNS Query Bytes

    REQUIRES: NODE VERSION ^12.0.0
    
    Example datagrams:
    a) 55750120000100000000000103313732033231370231310331373400000100010000291000000000000000 (172.217.11.174)
    b) b3a5012000010000000000010331353103313031033132390331343000000100010000291000000000000000 (151.101.129.140)
    c) 3ed201200001000000000001023133023333033232390331323900000100010000291000000000000000 (13.33.229.129)
*/

if (process.argv.length !== 4) {
  throw new Error('HOST AND PORT ARGUMENTS NEEDED!');
}

const chalk = require('chalk');
const host = process.argv[2];
const port = process.argv[3];
const client = require('dgram').createSocket({
  type: 'udp4',
  recvBufferSize: 4096,
  sendBufferSize: 4096,
});

client.on('error', error => {
  console.info(chalk.red('ERROR from Datagram Socket:'));
  console.error(error);
});

client.on('listening', () => {
  const { address, port } = client.address();
  console.info(chalk.cyan('LISTENING: ') + `${address}:${port}`);
});

client.on('connect', s => {
  console.info(chalk.green('NEW CONNECTION'));
});

client.on('message', (message, req) => {
  console.info(chalk.yellow('MESSAGE FROM :') + `${req.address}:${req.port}`);
  console.log(message);
});

client.on('close', () => {
  console.info(chalk.gray('CONNECTION CLOSED'));
});

client.connect(port, host, error => {
  if (error) {
    console.info(
      chalk.red('ERROR: ') + `attempting to connect to ${host}:${port}`,
    );
    return console.error(error);
  }
  const rl = require('readline').createInterface({
    input: process.stdin,
    terminal: false,
  });

  rl.on('line', line => {
    client.send(Buffer.from(line.trim(), 'hex'), (error, bytes) => {
      if (error) {
        console.info(
          chalk.red('ERROR: ') +
            `attempting to send datagram to ${host}:${port}`,
        );
        return console.error(error);
      }
      console.info(chalk.yellow('BYTES RECEIVED:'));
      console.log(bytes);
    });
  });

  rl.on('close', () => {
    client.close();
  });

  console.log('Enter a valid dns message below(bytes):');
});
