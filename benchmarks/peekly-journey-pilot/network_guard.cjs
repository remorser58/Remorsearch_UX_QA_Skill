'use strict';
// This process-local guard protects owned Node experiments, not the user's runtime.
const fs = require('node:fs');
const deny = (operation) => function () {
  if (process.env.PEEKLY_PILOT_NETWORK_LOG) {
    fs.appendFileSync(process.env.PEEKLY_PILOT_NETWORK_LOG,
      JSON.stringify({ operation, blocked: true }) + '\n', { mode: 0o600 });
  }
  const error = new Error('External or listening network activity is outside this pilot');
  error.name = 'PeeklyPilotNetworkDenied';
  throw error;
};
for (const [module, names] of [
  ['node:http', ['request', 'get']],
  ['node:https', ['request', 'get']],
  ['node:net', ['connect', 'createConnection']],
  ['node:tls', ['connect']],
]) {
  const target = require(module);
  for (const name of names) target[name] = deny(module + '.' + name);
}
require('node:net').Server.prototype.listen = deny('net.Server.listen');
globalThis.fetch = deny('fetch');
globalThis.WebSocket = deny('WebSocket');
