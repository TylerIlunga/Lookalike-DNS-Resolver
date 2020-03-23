/* 
    Client for One-Shot DNS Server using Standard DNS Query Bytes

    REQUIRES: NODE VERSION ^12.0.0
    
    Example datagrams:
    a) 28be012000010000000000000462696e6703636f6d0000010001 (bing)
    b) 02f2012000010000000000000866616365626f6f6b03636f6d0000010001 (facebook)
    c) 6a0601200001000000000000047562657203636f6d0000010001(uber)
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
