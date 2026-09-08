# Google Vertex AI Agent Engine & GenAI SDK Integration

## Architecture & Separation of Concerns
Studio Guardian explicitly complies with Constitution Principle 1 (Vertex AI is the Agent Runtime) and Principle 2 (Gemini is the Reasoning Layer):
`Application -> Vertex AI Agent Engine Runtime -> Incident Commander -> Specialist Agents -> Tools/MCP -> Decisions/Actions`

## Truthful Runtime Metadata Exposed
The backend and frontend Command Center truthfully reflect real runtime state:
- **Agent Runtime**: `Vertex AI Agent Engine (Cloud Active)` or `Deterministic Local Runtime (Vertex AI SDK Fallback)`
- **Model**: `gemini-2.5-flash` / `gemini-1.5-pro`
- **Project & Location**: `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION`
- **Session ID**: Active session trace frame (e.g., `session-pred-...`)
- **Active Specialist**: `PredictiveRiskAgent`, `AdIntegrityAgent`, `PerceptualQualitySentinel`, `BusinessImpactAgent`, `SafetyDirector`

## Structured Output Validation
All specialist agents enforce Pydantic v2 structured output schemas. Vertex AI compatibility is maintained by recursive stripping of `additionalProperties` and using `types.GenerateContentConfig(response_mime_type="application/json", response_schema=...)`.