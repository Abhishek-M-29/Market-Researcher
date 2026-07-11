const flowConfig = {
  "id": "d174af12-8a98-44da-8ddc-a182ec5d1f20",
  "name": "Flow 2 RAG Query GraphQLREST API",
  "edges": [
    {
      "id": "triggerNode_1-memoryRetrieveNode_1",
      "type": "defaultEdge",
      "source": "triggerNode_1",
      "target": "memoryRetrieveNode_1",
      "sourceHandle": "bottom",
      "targetHandle": "top"
    },
    {
      "id": "memoryRetrieveNode_1-searchNode_1",
      "type": "defaultEdge",
      "source": "memoryRetrieveNode_1",
      "target": "searchNode_1",
      "sourceHandle": "bottom",
      "targetHandle": "top"
    },
    {
      "id": "searchNode_1-LLMNode_1",
      "type": "defaultEdge",
      "source": "searchNode_1",
      "target": "LLMNode_1",
      "sourceHandle": "bottom",
      "targetHandle": "top"
    },
    {
      "id": "memoryRetrieveNode_1-LLMNode_1",
      "type": "defaultEdge",
      "source": "memoryRetrieveNode_1",
      "target": "LLMNode_1",
      "sourceHandle": "bottom",
      "targetHandle": "top"
    },
    {
      "id": "LLMNode_1-memoryNode_1",
      "type": "defaultEdge",
      "source": "LLMNode_1",
      "target": "memoryNode_1",
      "sourceHandle": "bottom",
      "targetHandle": "top"
    },
    {
      "id": "memoryNode_1-responseNode_triggerNode_1",
      "type": "defaultEdge",
      "source": "memoryNode_1",
      "target": "responseNode_triggerNode_1",
      "sourceHandle": "bottom",
      "targetHandle": "top"
    },
    {
      "id": "response-responseNode_triggerNode_1",
      "type": "responseEdge",
      "source": "triggerNode_1",
      "target": "responseNode_triggerNode_1",
      "sourceHandle": "to-response",
      "targetHandle": "from-trigger"
    }
  ],
  "status": "active",
  "created_at": "2026-07-09T04:48:47.002286+00:00",
  "trigger_id": null,
  "nodes": [
    {
      "id": "memoryRetrieveNode_1",
      "data": {
        "logic": [],
        "modes": {},
        "nodeId": "memoryRetrieveNode",
        "schema": {
          "memories": "object",
          "rawMemories": "object"
        },
        "values": {
          "id": "memoryRetrieveNode_1",
          "limit": 5,
          "filters": [],
          "nodeName": "Memory Retrieve",
          "searchQuery": "workflow.triggerNode_1.output.query",
          "memoryCollection": "rag_memory",
          "embeddingModelName": [
            {
              "type": "embedder/text",
              "params": {},
              "configName": "configA",
              "model_name": "text-embedding-3-small",
              "credentialId": "PLACEHOLDER",
              "provider_name": "openai",
              "credential_name": "OPENAI_KEY"
            }
          ]
        }
      },
      "type": "dynamicNode",
      "position": {
        "x": 0,
        "y": 0
      },
      "draggable": false
    },
    {
      "id": "searchNode_1",
      "data": {
        "logic": [],
        "modes": {},
        "nodeId": "searchNode",
        "schema": {},
        "values": {
          "id": "searchNode_1",
          "topK": 5,
          "query": "workflow.triggerNode_1.output.query",
          "filters": [],
          "nodeName": "Vector Search",
          "vectorCollection": "rag_documents",
          "embeddingModelName": [
            {
              "type": "embedder/text",
              "params": {},
              "configName": "configA",
              "model_name": "text-embedding-3-small",
              "credentialId": "PLACEHOLDER",
              "provider_name": "openai",
              "credential_name": "OPENAI_KEY"
            }
          ]
        }
      },
      "type": "dynamicNode",
      "position": {
        "x": 0,
        "y": 0
      },
      "draggable": false
    },
    {
      "id": "LLMNode_1",
      "data": {
        "logic": [],
        "modes": {},
        "nodeId": "LLMNode",
        "schema": {
          "_meta": "object",
          "images": "object",
          "tool_calls": "object",
          "generatedResponse": "string"
        },
        "values": {
          "id": "LLMNode_1",
          "tools": [],
          "prompts": [
            {
              "id": "15950185-c147-488f-a386-0001da199625",
              "role": "system",
              "content": "You are a helpful assistant. Answer the user's question using ONLY the provided document context below. If the answer is not found in the context, say so clearly. Cite relevant sources where possible.\n\nDocument Context:\nworkflow.searchNode_1.output\n\nConversation Memory:\nworkflow.memoryRetrieveNode_1.output.memories"
            },
            {
              "id": "a122be14-57a9-4743-937a-1ca6fc0b8e44",
              "role": "user",
              "content": "workflow.triggerNode_1.output.query"
            }
          ],
          "memories": "workflow.memoryRetrieveNode_1.output.memories",
          "messages": "[]",
          "nodeName": "Generate Response",
          "attachments": "",
          "credentials": "",
          "generativeModelName": [
            {
              "type": "generator/text",
              "params": {},
              "configName": "configA",
              "model_name": "gpt-4o",
              "credentialId": "PLACEHOLDER",
              "provider_name": "openai",
              "credential_name": "OPENAI_KEY"
            }
          ]
        }
      },
      "type": "dynamicNode",
      "position": {
        "x": 0,
        "y": 0
      },
      "draggable": false
    },
    {
      "id": "memoryNode_1",
      "data": {
        "logic": [],
        "modes": {},
        "nodeId": "memoryNode",
        "schema": {
          "memoryActions": "object",
          "extractedFacts": "object"
        },
        "values": {
          "id": "memoryNode_1",
          "metadata": "{\"source\": \"rag_pipeline\", \"sessionId\": \"workflow.triggerNode_1.output.sessionId\"}",
          "nodeName": "Memory Add",
          "uniqueId": "workflow.triggerNode_1.output.sessionId",
          "sessionId": "workflow.triggerNode_1.output.sessionId",
          "memoryValue": {
            "userMessage": "workflow.triggerNode_1.output.query",
            "assistantMessage": "workflow.LLMNode_1.output.generatedResponse"
          },
          "memoryCollection": "rag_memory",
          "embeddingModelName": [
            {
              "type": "embedder/text",
              "params": {},
              "configName": "configA",
              "model_name": "text-embedding-3-small",
              "credentialId": "PLACEHOLDER",
              "provider_name": "openai",
              "credential_name": "OPENAI_KEY"
            }
          ],
          "generativeModelName": [
            {
              "type": "generator/text",
              "params": {},
              "configName": "configA",
              "model_name": "gpt-4o",
              "credentialId": "PLACEHOLDER",
              "provider_name": "openai",
              "credential_name": "OPENAI_KEY"
            }
          ]
        }
      },
      "type": "dynamicNode",
      "position": {
        "x": 0,
        "y": 0
      },
      "draggable": false
    },
    {
      "id": "triggerNode_1",
      "data": {
        "modes": {},
        "nodeId": "graphqlNode",
        "schema": {
          "query": "string",
          "sessionId": "string"
        },
        "values": {
          "id": "triggerNode_1",
          "nodeName": "API Request",
          "responeType": "realtime",
          "advance_schema": "{\n  \"query\": \"string\",\n  \"sessionId\": \"string\"\n}"
        },
        "trigger": true
      },
      "type": "triggerNode",
      "position": {
        "x": 0,
        "y": 0
      }
    },
    {
      "id": "responseNode_triggerNode_1",
      "data": {
        "modes": {},
        "nodeId": "graphqlResponseNode",
        "schema": {},
        "values": {
          "id": "responseNode_triggerNode_1",
          "headers": "{\"content-type\": \"application/json\"}",
          "retries": "0",
          "nodeName": "API Response",
          "webhookUrl": "",
          "retry_delay": "0",
          "outputMapping": "{\"answer\": \"workflow.LLMNode_1.output.generatedResponse\", \"sessionId\": \"workflow.triggerNode_1.output.sessionId\"}"
        }
      },
      "type": "responseNode",
      "position": {
        "x": 0,
        "y": 0
      }
    }
  ]
};

export async function getNodesAndEdges(): Promise<{
    nodes: Record<string, any>[],
    edges: Record<string, any>[],
}> {
    return {
        nodes: flowConfig.nodes,
        edges: flowConfig.edges,
    }
}

export async function getFlowConfig(): Promise<Record<string, any>> {
    return flowConfig;
}