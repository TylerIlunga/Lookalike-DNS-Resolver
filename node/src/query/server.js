require('dotenv').config();

//  USE dig [HOST NAME] @127.0.0.1 +noedns
//  Avoids "malformed" packages messages do to EDNS V0
//  Due to changes to the original DNS protocol

//  bing.com A 172.217.11.174(google.com)
//  facebook.com A 151.101.129.140(reddit)
//  uber.com A 13.33.229.129(lyft)

const chalk = require('chalk');
const server = require('dgram').createSocket({
  type: 'udp4',
  recvBufferSize: 4096,
  sendBufferSize: 4096,
});
const DNS_ZONE_MAP = {
  'bing.com': Buffer.from('ACD90BAE', 'hex'),
  'facebook.com': Buffer.from('9765818C', 'hex'),
  'uber.com': Buffer.from('0D21E581', 'hex'),
};

class MainHandler {
  constructor() {}

  handle(datagram, reqInfo) {
    const Conn = new Connection(server, reqInfo.address, reqInfo.port);
    console.log(
      chalk.yellow('HANDLING:') +
        ` ${Conn.getClientAddr()}'s request on Process ${process.pid}`,
    );
    console.log(chalk.yellow('DATAGRAM RECEIVED (bytes)'));
    console.log(datagram);
    Conn.response(new DNSMessage(datagram).toResponse());
  }
}

class Connection {
  constructor(socket, host, port) {
    this.socket = socket;
    this.client = {
      host,
      port,
    };
  }

  getSocket() {
    return this.socket;
  }

  getClientAddr() {
    return `${this.client.host}:${this.client.port}`;
  }

  response(data) {
    this.socket.send(
      data,
      0,
      data.length,
      this.client.port,
      this.client.host,
      (error, bytes) => {
        if (error) {
          console.log(
            chalk.red('ERROR: ') +
              `attempting to response to client ${this.getClientAddr()}`,
          );
          return console.error(error);
        }
        console.log(
          chalk.yellow(`Received ${bytes} BYTES FROM :`),
          this.getClientAddr(),
        );
      },
    );
  }
}

class DNSMessage {
  constructor(byteMsgBuffer) {
    this.msgHeader = {};
    this.msgQuestion = {};
    this.msgAnswer = {};
    this.parseMessage(byteMsgBuffer);
  }

  parseMessage(byteMsgBuffer) {
    console.log('parsing datagram...');
    this.extractHeader(byteMsgBuffer.subarray(0, 12));
    this.extractQuestion(byteMsgBuffer.subarray(12, byteMsgBuffer.length));
    this.buildAnswer();
  }

  extractHeader(headerBuffer) {
    console.log('extracting header bytes...');
    console.log('Header(bytes):', headerBuffer);
    const messageIdBytes = headerBuffer.subarray(0, 2);
    const qrCode = 1; // Query ==> Response
    const opCode = 0; // Standard query
    const aa = 1; // Authorativie answer
    const tc = 0; // No Truncation
    const rd = 1; // Recursion will be desired
    const ra = 1; // If Recursion is desired, recursion should be available
    const z = 0; // No extra zeros
    const rCode = 0; // Response Code: Error will be thrown if one exists

    const questionRecordsCount = headerBuffer.subarray(4, 6);
    const originalAnswerRecordsCount = headerBuffer.subarray(6, 8);
    const originalNSRecordsCount = headerBuffer.subarray(8, 10);
    const originalARRecordsCount = headerBuffer.subarray(10, 12);

    const qrOpCodeAATCRDBytes = Buffer.from('85', 'hex'); // QR, OpCode(Q), AA, TC, and RD bits(1000 0101)
    const raZRcodeBytes = Buffer.from('80', 'hex'); // RA, Z, and RCode bits(1000 0000)
    const anCountBytes = Buffer.from('0001', 'hex'); // ANCount
    const nsCountBytes = Buffer.from('0000', 'hex'); // NSCount
    const arCountBytes = Buffer.from('0000', 'hex'); // ARCount

    let headerAsBytes = Buffer.from([]);
    headerAsBytes = Buffer.concat(
      [headerAsBytes, messageIdBytes],
      headerAsBytes.length + messageIdBytes.length,
    );
    headerAsBytes = Buffer.concat(
      [headerAsBytes, qrOpCodeAATCRDBytes],
      headerAsBytes.length + qrOpCodeAATCRDBytes.length,
    );
    headerAsBytes = Buffer.concat(
      [headerAsBytes, raZRcodeBytes],
      headerAsBytes.length + raZRcodeBytes.length,
    );
    headerAsBytes = Buffer.concat(
      [headerAsBytes, questionRecordsCount],
      headerAsBytes.length + questionRecordsCount.length,
    );
    headerAsBytes = Buffer.concat(
      [headerAsBytes, anCountBytes],
      headerAsBytes.length + anCountBytes.length,
    );
    headerAsBytes = Buffer.concat(
      [headerAsBytes, nsCountBytes],
      headerAsBytes.length + nsCountBytes.length,
    );
    headerAsBytes = Buffer.concat(
      [headerAsBytes, arCountBytes],
      headerAsBytes.length + arCountBytes.length,
    );

    this.msgHeader = {
      aa,
      tc,
      rd,
      ra,
      z,
      rCode,
      bytes: headerAsBytes,
      id: messageIdBytes,
      qrCode: qrCode,
      opCode: opCode,
      qdCount: questionRecordsCount,
      anCount: originalAnswerRecordsCount,
      nscount: originalNSRecordsCount,
      arcount: originalARRecordsCount,
    };

    console.log('this.msgHeader:', this.msgHeader);
  }

  extractQuestion(buffer) {
    console.log('extracting question bytes...');
    console.log('Question (bytes):', buffer);
    let qnameBytesOffset = 0;

    for (const answerByte of buffer) {
      if (answerByte === 0) {
        break;
      }
      qnameBytesOffset += 8;
    }

    qnameBytesOffset = Math.floor(qnameBytesOffset / 8);

    const qname = buffer.subarray(0, qnameBytesOffset + 1);
    const qtype = buffer.subarray(qnameBytesOffset + 1, qnameBytesOffset + 3);
    const qclass = buffer.subarray(qnameBytesOffset + 3, qnameBytesOffset + 5);
    const aaRecords = buffer.subarray(qnameBytesOffset + 5, buffer.length);

    this.msgQuestion = {
      qname,
      qtype,
      qclass,
      additional: aaRecords,
      bytes: buffer,
    };

    console.log('this.msgQuestion:', this.msgQuestion);
  }

  buildAnswer() {
    console.log('building answer...');
    let newQnameBuffer = Buffer.from([]);
    const asciiPeriodAsHexBuffer = Buffer.from('2E', 'hex');

    let index = 0;
    for (const byte of this.msgQuestion.qname) {
      if (index === 0 || byte === 0) {
        index++;
        continue;
      }
      if (byte !== 0 && (byte < 33 || byte > 172)) {
        newQnameBuffer = Buffer.concat(
          [newQnameBuffer, asciiPeriodAsHexBuffer],
          newQnameBuffer.length + asciiPeriodAsHexBuffer.length,
        );
        index++;
        continue;
      }
      const byteAsBuffer = Buffer.from([byte]);
      newQnameBuffer = Buffer.concat(
        [newQnameBuffer, byteAsBuffer],
        newQnameBuffer.length + byteAsBuffer.length,
      );
      index++;
    }

    const qnameAscii = newQnameBuffer.toString('ascii');
    const domainIpTmpMap = { [qnameAscii]: Buffer.from('00000000', 'hex') };
    Object.keys(DNS_ZONE_MAP).forEach(domain => {
      if (domainIpTmpMap[domain] !== undefined) {
        domainIpTmpMap[domain] = DNS_ZONE_MAP[domain];
      }
    });

    this.msgAnswer = {
      name: this.msgQuestion.qname,
      type: Buffer.from('0001', 'hex'),
      class: Buffer.from('0001', 'hex'),
      ttl: Buffer.from('0000003C', 'hex'),
      rdlength: Buffer.from('0004', 'hex'),
      rdata: domainIpTmpMap[qnameAscii],
    };

    console.log('this.msgAnswer', this.msgAnswer);
  }

  getMessage() {
    return {
      header: this.msgHeader,
      question: this.msgQuestion,
      answer: this.msgAnswer,
      authority: {},
      additional: {},
    };
  }

  toResponse() {
    const message = this.getMessage();
    const headerBytes = Buffer.from(message.header.bytes);
    const questionBytes = Buffer.from(message.question.bytes);
    let response = Buffer.concat(
      [headerBytes, questionBytes],
      headerBytes.length + questionBytes.length,
    );

    Object.values(message.answer).forEach(buffer => {
      response = Buffer.concat(
        [response, buffer],
        response.length + buffer.length,
      );
    });

    console.log('response:', response);
    return response;
  }
}

const MessageHandler = new MainHandler();

server.on('error', error => {
  console.log(chalk.red('ERROR from Datagram Socket:'));
  console.error(error);
});

server.on('listening', () => {
  const { address, port } = server.address();
  console.log(chalk.cyan('LISTENING: ') + `${address}:${port}`);
});

server.on('connect', s => {
  console.log(chalk.green('NEW CONNECTION'));
});

server.on('message', (message, req) => {
  console.log(chalk.yellow('MESSAGE FROM: ') + `${req.address}:${req.port}`);
  console.log(message);
  MessageHandler.handle(message, req);
});

server.on('close', () => {
  console.log(chalk.gray('CONNECTION CLOSED'));
});

server.bind(process.env.SERVER_PORT);
