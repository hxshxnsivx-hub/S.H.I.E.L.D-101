# @kavach/client

JavaScript/TypeScript client for the **Kavach** agent data-firewall. Node/TS
agents protect their outbound tool calls by calling a running Kavach service
(`kavach[service]`, see the main repo).

```js
import { KavachClient } from "@kavach/client";

const kavach = new KavachClient("http://localhost:8080");

// guard a tool call's arguments before you dispatch it
const { sanitized, status } = await kavach.guardArguments("crm_api", {
  summary: "Aadhaar 2345-6789-0124, card 4111 1111 1111 1111",
  amount: 500,
});
await crmApi.create(sanitized); // sends tokenised/blocked data only
```

Requires Node 18+ (global `fetch`). For Python in-process use, use the Python SDK.
