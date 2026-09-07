import type { Edge } from '@xyflow/react';
import type { CustomNode } from '../types';

export interface WorkflowPreset {
  id: string;
  name: string;
  description: string;
  defaultInput: string;
  nodes: CustomNode[];
  edges: Edge[];
}

export const PRESETS: WorkflowPreset[] = [
  {
    id: "support-triage",
    name: "Customer Support & Urgent Escalation",
    description: "Evaluates inbound tickets, checks for technical severity, and branches to P1 on-call or standard queue.",
    defaultInput: "CRITICAL: The production database cluster is down with 500 error code for all checkout requests!",
    nodes: [
      {
        id: "start",
        type: "start",
        position: { x: 250, y: 30 },
        data: { label: "Inbound Ticket", prompt: "", node_type: "start", status: "idle" },
      },
      {
        id: "node-1",
        type: "decision",
        position: { x: 200, y: 150 },
        data: {
          label: "Issue Type Check",
          prompt: "Is this inquiry describing a technical bug, system error, or outage?",
          node_type: "decision",
          status: "idle",
        },
      },
      {
        id: "node-urgent",
        type: "decision",
        position: { x: 50, y: 360 },
        data: {
          label: "Severity Evaluator",
          prompt: "Is the issue critical, affecting production availability or payments?",
          node_type: "decision",
          status: "idle",
        },
      },
      {
        id: "node-sales",
        type: "decision",
        position: { x: 420, y: 360 },
        data: {
          label: "Sales Intent Check",
          prompt: "Is the user inquiring about enterprise pricing, licenses, or purchasing?",
          node_type: "decision",
          status: "idle",
        },
      },
      {
        id: "end-p1",
        type: "end",
        position: { x: -20, y: 560 },
        data: { label: "🚨 P1 On-Call Escalation", prompt: "", node_type: "end", status: "idle" },
      },
      {
        id: "end-support-l2",
        type: "end",
        position: { x: 180, y: 560 },
        data: { label: "🛠️ Standard Support Queue", prompt: "", node_type: "end", status: "idle" },
      },
      {
        id: "end-sales",
        type: "end",
        position: { x: 380, y: 560 },
        data: { label: "💼 Enterprise Sales Rep", prompt: "", node_type: "end", status: "idle" },
      },
      {
        id: "end-general",
        type: "end",
        position: { x: 580, y: 560 },
        data: { label: "📫 General Info Team", prompt: "", node_type: "end", status: "idle" },
      },
    ],
    edges: [
      { id: "e-start", source: "start", target: "node-1", type: "smoothstep" },
      { id: "e1-yes", source: "node-1", target: "node-urgent", sourceHandle: "yes", label: "YES", type: "smoothstep", style: { stroke: "#10b981", strokeWidth: 2 } },
      { id: "e1-no", source: "node-1", target: "node-sales", sourceHandle: "no", label: "NO", type: "smoothstep", style: { stroke: "#ef4444", strokeWidth: 2 } },
      { id: "e-urg-yes", source: "node-urgent", target: "end-p1", sourceHandle: "yes", label: "YES", type: "smoothstep", style: { stroke: "#10b981", strokeWidth: 2 } },
      { id: "e-urg-no", source: "node-urgent", target: "end-support-l2", sourceHandle: "no", label: "NO", type: "smoothstep", style: { stroke: "#ef4444", strokeWidth: 2 } },
      { id: "e-sales-yes", source: "node-sales", target: "end-sales", sourceHandle: "yes", label: "YES", type: "smoothstep", style: { stroke: "#10b981", strokeWidth: 2 } },
      { id: "e-sales-no", source: "node-sales", target: "end-general", sourceHandle: "no", label: "NO", type: "smoothstep", style: { stroke: "#ef4444", strokeWidth: 2 } },
    ],
  },
  {
    id: "content-moderation",
    name: "Automated Content & Toxicity Filter",
    description: "Evaluates user-generated content for toxicity, spam, and commercial advertising.",
    defaultInput: "Buy cheap crypto coins now at http://fake-scam-link.xyz with 1000x guaranteed return!",
    nodes: [
      {
        id: "start",
        type: "start",
        position: { x: 250, y: 30 },
        data: { label: "User Submission", prompt: "", node_type: "start", status: "idle" },
      },
      {
        id: "mod-1",
        type: "decision",
        position: { x: 200, y: 150 },
        data: {
          label: "Spam / Promotion Check",
          prompt: "Does this text contain unsolicited promotional spam, scam links, or advertising?",
          node_type: "decision",
          status: "idle",
        },
      },
      {
        id: "mod-tox",
        type: "decision",
        position: { x: 380, y: 360 },
        data: {
          label: "Toxicity / Harassment",
          prompt: "Does this text contain hateful, abusive, or profane language?",
          node_type: "decision",
          status: "idle",
        },
      },
      {
        id: "end-block-spam",
        type: "end",
        position: { x: 50, y: 360 },
        data: { label: "🚫 Auto-Reject (Spam)", prompt: "", node_type: "end", status: "idle" },
      },
      {
        id: "end-block-tox",
        type: "end",
        position: { x: 250, y: 550 },
        data: { label: "⛔ Auto-Reject (Toxicity)", prompt: "", node_type: "end", status: "idle" },
      },
      {
        id: "end-approve",
        type: "end",
        position: { x: 480, y: 550 },
        data: { label: "✅ Approved & Published", prompt: "", node_type: "end", status: "idle" },
      },
    ],
    edges: [
      { id: "em-start", source: "start", target: "mod-1", type: "smoothstep" },
      { id: "em1-yes", source: "mod-1", target: "end-block-spam", sourceHandle: "yes", label: "YES", type: "smoothstep", style: { stroke: "#10b981", strokeWidth: 2 } },
      { id: "em1-no", source: "mod-1", target: "mod-tox", sourceHandle: "no", label: "NO", type: "smoothstep", style: { stroke: "#ef4444", strokeWidth: 2 } },
      { id: "em2-yes", source: "mod-tox", target: "end-block-tox", sourceHandle: "yes", label: "YES", type: "smoothstep", style: { stroke: "#10b981", strokeWidth: 2 } },
      { id: "em2-no", source: "mod-tox", target: "end-approve", sourceHandle: "no", label: "NO", type: "smoothstep", style: { stroke: "#ef4444", strokeWidth: 2 } },
    ],
  },
];
