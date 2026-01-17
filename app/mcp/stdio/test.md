{
  "mcpServers": {
    "amap-maps-streamableHTTP": {
      "url": "https://mcp.amap.com/mcp?key=a2854b8c97e16885f90e697d0c121bcb"
    },
    "github": {
      "type": "sse",
      "url": "https://mcp.api-inference.modelscope.net/7682e2fede954d/sse"
    },
    "playwright": {
      "command": "npx",
      "args": ["-y", "@executeautomation/playwright-mcp-server"]
    }
  }
}
