const flowConfig = {
  "id": "d988c414-2e7f-4264-86ed-9582a5e3a966",
  "name": "Flow 1 Document Indexing Google Drive",
  "edges": [
    {
      "id": "googleDriveNode_trigger_1-extractFromFileNode_1",
      "type": "defaultEdge",
      "source": "googleDriveNode_trigger_1",
      "target": "extractFromFileNode_1",
      "sourceHandle": "bottom",
      "targetHandle": "top"
    },
    {
      "id": "extractFromFileNode_1-chunkNode_1",
      "type": "defaultEdge",
      "source": "extractFromFileNode_1",
      "target": "chunkNode_1",
      "sourceHandle": "bottom",
      "targetHandle": "top"
    },
    {
      "id": "chunkNode_1-vectorizeNode_1",
      "type": "defaultEdge",
      "source": "chunkNode_1",
      "target": "vectorizeNode_1",
      "sourceHandle": "bottom",
      "targetHandle": "top"
    },
    {
      "id": "vectorizeNode_1-vectorNode_1",
      "type": "defaultEdge",
      "source": "vectorizeNode_1",
      "target": "vectorNode_1",
      "sourceHandle": "bottom",
      "targetHandle": "top"
    }
  ],
  "status": "active",
  "created_at": "2026-07-09T04:48:43.446675+00:00",
  "trigger_id": null,
  "nodes": [
    {
      "id": "extractFromFileNode_1",
      "data": {
        "logic": [],
        "modes": {},
        "nodeId": "extractFromFileNode",
        "schema": {
          "outputSchema": {
            "files": "object"
          }
        },
        "values": {
          "id": "extractFromFileNode_1",
          "trim": false,
          "ltrim": false,
          "quote": "\"",
          "rtrim": false,
          "format": "auto",
          "comment": "null",
          "fileUrl": "{{googleDriveNode_trigger_1.document_key}}",
          "headers": true,
          "maxRows": 0,
          "encoding": "utf8",
          "nodeName": "Extract From File",
          "password": "",
          "skipRows": 0,
          "delimiter": ",",
          "joinPages": true,
          "ignoreEmpty": false,
          "returnRawText": false,
          "encodeAsBase64": false,
          "discardUnmappedColumns": false
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
      "id": "chunkNode_1",
      "data": {
        "logic": [],
        "modes": {},
        "nodeId": "chunkNode",
        "schema": {
          "outputSchema": {
            "chunks": "string"
          }
        },
        "values": {
          "id": "chunkNode_1",
          "nodeName": "Chunk Text",
          "chunkField": "{{extractFromFileNode_1.files}}",
          "numOfChars": 512,
          "separators": [
            "\n\n",
            "\n",
            " "
          ],
          "chunkingType": "recursiveCharacterTextSplitter",
          "overlapChars": 50
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
      "id": "vectorizeNode_1",
      "data": {
        "logic": [],
        "modes": {},
        "nodeId": "vectorizeNode",
        "schema": {
          "outputSchema": {
            "_meta": "object",
            "vectors": "object"
          }
        },
        "values": {
          "id": "vectorizeNode_1",
          "nodeName": "Vectorize Chunks",
          "inputText": "{{chunkNode_1.chunks}}",
          "embeddingModelName": [
            {
              "type": "embedder/text",
              "params": {},
              "configName": "configA",
              "model_name": "text-embedding-3-small",
              "credentialId": "PLACEHOLDER",
              "provider_name": "openai",
              "credential_name": "PLACEHOLDER"
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
      "id": "vectorNode_1",
      "data": {
        "logic": [],
        "modes": {},
        "nodeId": "vectorNode",
        "schema": {
          "outputSchema": {
            "message": "string",
            "recordsIndexed": "string",
            "duplicateRecordsDeleted": "string"
          }
        },
        "values": {
          "id": "vectorNode_1",
          "action": "index",
          "nodeName": "Index to VectorDB",
          "vectorDB": "PLACEHOLDER_VECTOR_DB",
          "primaryKeys": [
            "source_file"
          ],
          "vectorsField": "{{vectorizeNode_1.vectors}}",
          "metadataField": "{\"source_file\": \"{{googleDriveNode_trigger_1.document_key}}\", \"content\": \"{{chunkNode_1.chunks}}\"}",
          "duplicateOperation": "overwrite"
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
      "id": "googleDriveNode_trigger_1",
      "data": {
        "modes": {},
        "nodeId": "googleDriveNode",
        "schema": {
          "outputSchema": {
            "content": "string",
            "document_key": "string"
          }
        },
        "values": {
          "id": "googleDriveNode_trigger_1",
          "globs": [
            "**"
          ],
          "nodeName": "Google Drive Trigger",
          "syncMode": "incremental_append",
          "folderUrl": "PLACEHOLDER_FOLDER_URL",
          "credentials": "PLACEHOLDER",
          "cronExpression": "0 0 00 ? * 1 * UTC"
        },
        "trigger": true
      },
      "type": "triggerNode",
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