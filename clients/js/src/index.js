// Kavach JS/TS client — talks to the Kavach service (gateway pattern).
// Node 18+ (global fetch). For Python-in-process use the Python SDK instead.

export class KavachClient {
  constructor(baseUrl = "http://localhost:8080") {
    this.baseUrl = baseUrl.replace(/\/+$/, "");
  }

  // Guard a raw text payload headed to `destination`.
  async guard(text, destination) {
    return this._post("/v1/guard", { text, destination });
  }

  // Guard a tool call's argument object (MCP / function-calling shape).
  async guardArguments(tool, args) {
    return this._post("/v1/guard-arguments", { tool, arguments: args });
  }

  async audit() {
    const r = await fetch(`${this.baseUrl}/v1/audit`);
    if (!r.ok) throw new Error(`Kavach /v1/audit -> ${r.status}`);
    return r.json();
  }

  async _post(path, body) {
    const r = await fetch(this.baseUrl + path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (!r.ok) throw new Error(`Kavach ${path} -> ${r.status}`);
    return r.json();
  }
}

export default KavachClient;
