# References

- [RFC 1035](https://www.ietf.org/rfc/rfc1035.txt)

# Steps

### Python

```
cd python
python -m venv env
source env/bin/activate
pip install -r requirements.txt
python src/query/server.py
*OPEN NEW TERMINAL*
python src/query/client.py localhost 53
```

### Node

```
cd node
nvm install 12.16.1 (or LTS)
npm i or npm install
python -m venv env
source env/bin/activate
pip install -r requirements.txt
node src/query/server.js
*OPEN NEW TERMINAL*
node src/query/client.js localhost 53
```

### DIG

1. Run Python or Node server
2. Execute `dig [HOST NAME] @127.0.0.1 +noedns`

### NSLOOKUP

1. Run Python or Node server
2. Execute `nslookup bing.com 127.0.0.1`
