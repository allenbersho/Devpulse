# DevPulse
## An Enterprise-Grade Agentic GitHub Intelligence Platform

Version: 2.0
Author: Allen
Status: Planning

---

# 1. Project Vision

DevPulse is an AI-powered GitHub Intelligence Platform that demonstrates how modern
Agentic AI systems are built using:

- Model Context Protocol (MCP)
- ReAct Agents
- LangGraph Multi-Agent Architecture
- A2A (Agent-to-Agent Communication)
- Live GitHub REST API
- Local or Cloud LLMs

Unlike simple GitHub chatbots, DevPulse acts as an intelligent engineering assistant capable of reasoning, planning, using tools, collaborating between agents, and exposing itself to external AI systems.

The primary goal is educational while still being designed similarly to production AI systems.

---

# 2. Problem Statement

Developers spend significant time searching GitHub for:

- Repository information
- Contributors
- Issues
- Release notes
- Project health
- Trending repositories

Instead of manually browsing GitHub, DevPulse provides a conversational interface capable of understanding natural language and retrieving live information directly from GitHub.

Example:

User:
Tell me about facebook/react

Instead of searching manually, DevPulse performs the API calls and summarizes the results intelligently.

---

# 3. Objectives

The project should demonstrate:

✓ Real MCP Server
✓ Tool Discovery
✓ Function Calling
✓ ReAct Agent
✓ Human-in-the-Loop
✓ LangGraph
✓ Multi-Agent Collaboration
✓ A2A Discovery
✓ Memory
✓ Real API Integration
✓ Production-ready Folder Structure

---

# 4. High Level Architecture

                    User
                      │
                      ▼
              Frontend (CLI/Web)
                      │
                      ▼
             DevPulse Controller
                      │
         ┌────────────┴────────────┐
         │                         │
         ▼                         ▼
   LangGraph Router          Conversation Memory
         │
         │
 ┌───────┼─────────────────────────────────┐
 │       │                 │               │
 ▼       ▼                 ▼               ▼
Repo   Issue Agent   Release Agent   Analytics Agent
Agent
 │
 └───────────────┬─────────────────────────┘
                 ▼
             MCP Client
                 │
                 ▼
             MCP Server
                 │
         GitHub Intelligence Tools
                 │
                 ▼
           GitHub REST API

---

# 5. Technology Stack

Backend
--------
Python

LLM
--------
Ollama
Groq
OpenAI

Frameworks
--------
LangGraph
FastMCP
OpenAI SDK

Libraries
--------
httpx
python-dotenv
rich
pydantic

Database
--------
SQLite (Conversation Storage)

Optional
--------
Redis
ChromaDB
FAISS

Frontend
--------
CLI
Streamlit
React

Deployment
--------
Docker
Render
Railway

---

# 6. Functional Requirements

The system shall:

✔ Search repositories

✔ View repository details

✔ List contributors

✔ List open issues

✔ Fetch release notes

✔ Remember previous repositories

✔ Route queries to specialist agents

✔ Publish Agent Card

✔ Support external A2A requests

✔ Work with multiple LLM providers

---

# 7. Project Phases

-----------------------------------------
PHASE 1
-----------------------------------------

Goal

Build a Real MCP Server.

Responsibilities

Expose GitHub as AI Tools.

Tools

search_repositories()

get_repo_details()

list_open_issues()

list_contributors()

get_latest_release()

Resource

github://repo/{owner}/{repo}/summary

Prompt

issue_triage_prompt()

Output

Working MCP Server

---

PHASE 2

Goal

Shared Infrastructure

Responsibilities

Create backend independent LLM interface.

Features

Switch between

Ollama

Groq

OpenAI

without changing code.

---

PHASE 3

Goal

Single Intelligent Agent

Architecture

User

↓

Reason

↓

Select Tool

↓

Human Approval

↓

Execute Tool

↓

Observe Result

↓

Final Response

Features

Conversation Memory

Tool Discovery

Reasoning Loop

Human Approval

---

PHASE 4

Goal

Multi-Agent System

Agents

Repository Agent

Issue Agent

Release Agent

Analytics Agent (NEW)

Security Agent (NEW)

Documentation Agent (NEW)

Workflow

Router

↓

Intent Classification

↓

Dispatch

↓

Specialist

↓

Return Answer

Each specialist has its own tools.

---

PHASE 5

Goal

Agent Discovery

Implement

Agent Card

Skills

Endpoints

Capability Discovery

External agents should discover DevPulse without knowing its internal implementation.

---

# 8. Proposed Folder Structure

DevPulse/

    docs/
        architecture.md
        api.md
        roadmap.md

    agents/
        repo_agent.py
        issue_agent.py
        release_agent.py
        analytics_agent.py
        security_agent.py
        documentation_agent.py

    mcp/
        mcp_server.py
        bridge.py
        resources.py
        prompts.py

    langgraph/
        graph.py
        router.py
        state.py

    models/
        model_client.py

    memory/
        sqlite_memory.py
        vector_memory.py

    tools/
        github_tools.py
        analytics_tools.py

    api/
        app.py

    frontend/
        streamlit_app.py

    tests/

    requirements.txt

---

# 9. Additional Features (My Suggestions)

## Repository Health Score

Generate

Overall Health

based on

Stars

Forks

Open Issues

Activity

Last Commit

Contributors

Score

0-100

---

## Security Analysis

Automatically report

Large number of vulnerabilities

Archived repository

Inactive project

Missing license

Missing README

---

## Contributor Insights

Generate

Top contributors

Contribution percentage

Bus factor

Contribution trend

---

## Issue Analytics

Categorize issues

Bug

Feature

Question

Documentation

Generate charts.

---

## Release Analyzer

Compare

Latest Release

Previous Release

Breaking Changes

Highlights

---

## Trending Repository Finder

Search

Python

AI

Machine Learning

Agentic AI

LLMs

Generate recommendations.

---

## Smart Repository Comparison

Example

Compare

LangGraph

CrewAI

AutoGen

Output

Stars

Issues

Activity

Contributors

License

Latest Release

Popularity

---

## AI Repository Recommendation

Example

"I want beginner Agentic AI repositories"

Return

Top repositories

Difficulty

Technologies

Popularity

Estimated learning time

---

## Conversation Memory

User

Tell me about LangGraph

Later

Who contributes the most?

The system should remember

LangGraph repository

without asking again.

---

## Report Generator

Generate

Markdown Report

PDF

HTML

Repository Summary

Engineering Report

---

## Dashboard

Streamlit Dashboard

Cards

Graphs

Repository Search

Issue Charts

Health Score

Contributor Graph

---

## API Layer

Expose

REST API

POST /chat

POST /search

POST /health

POST /compare

GET /repo

This allows any frontend to use DevPulse.

---

## Authentication

Optional GitHub OAuth

Store user preferences

Private repository support

---

# 10. Future Scope

Integrate

GitHub Actions

Jira

Slack

Linear

Notion

Azure DevOps

Docker Hub

CI/CD systems

---

# 11. Learning Outcomes

After completing DevPulse, a developer should understand

✓ MCP

✓ Tool Calling

✓ Function Calling

✓ LangGraph

✓ ReAct

✓ Human-in-the-Loop

✓ A2A

✓ GitHub APIs

✓ Multi-Agent Systems

✓ Conversation Memory

✓ AI Architecture

✓ Production Design

---

# 12. End-to-End Workflow

User

↓

Frontend

↓

Router Agent

↓

Intent Classification

↓

Specialist Agent

↓

MCP Client

↓

MCP Server

↓

GitHub API

↓

Tool Result

↓

LLM Reasoning

↓

Natural Language Response

↓

Frontend

---

# 13. Success Criteria

The project is considered complete when:

✓ Users can query GitHub naturally.

✓ Live GitHub APIs are used.

✓ MCP tools are dynamically discovered.

✓ Agents collaborate correctly.

✓ Router dispatches accurately.

✓ Memory works across conversations.

✓ Human approval works before tool execution.

✓ Agent Card is discoverable.

✓ Reports can be generated.

✓ Project can be deployed using Docker.

---

# Final Vision

DevPulse should evolve beyond a classroom demonstration into a production-inspired AI platform. By combining MCP for standardized tool access, LangGraph for orchestrating specialized agents, ReAct for deliberate reasoning, and A2A for interoperability, the project demonstrates how modern AI assistants can be modular, extensible, and capable of integrating with real-world developer workflows. The long-term goal is to create a reusable foundation that can expand beyond GitHub into broader engineering ecosystems while remaining easy to understand and extend.