Back-End System Specification: "Echoes of Mercy" Server
Overview
The "Echoes of Mercy" back-end is a scalable Python server responsible for dynamic content generation and orchestration for the Godot VR client. It handles AI-driven narrative elements (e.g., child dialogue via LLM), emotional TTS synthesis, story branching based on user choices, session persistence, and now an AI-driven 3D model generator for procedural assets. This enables runtime customization, such as generating vignette-specific 3D models (e.g., war-damaged furniture or ethereal memory actors) from text prompts derived from the story context.
The server supports low-latency responses (<50ms for dialogue, <5s for 3D gen) via async processing and caching. It communicates with the client over HTTP/REST for initial loads and WebSockets for real-time streaming (e.g., live TTS audio or model metadata). Designed for deployment on cloud (e.g., AWS EC2 or Vercel) with auto-scaling for multiple users.
Core Goals:

Ensure emotional fidelity: AI outputs must align with child-like phrasing and war-trauma themes.
Procedural generation: 3D models adapt to user choices (e.g., if Gavel is selected, generate judicial-themed artifacts).
Security: Rate-limit API calls; anonymize user data; no persistent storage of imprints.

Assumptions:

Client sends user choices (e.g., character select) via JSON payloads.
3D models output as GLTF (lightweight, Godot-compatible); pre-process for VR optimization (e.g., LODs via Blender API).
Free-tier limits respected (e.g., Hugging Face inference quota); fallback to pre-generated assets.

Technical Stack (Server-Side)

Framework: FastAPI (async API, auto-docs via Swagger; WebSocket support).
Database: PostgreSQL (via SQLAlchemy ORM) for story branches, user sessions, and cached AI outputs; Redis for ephemeral caching (e.g., active dialogues).
AI Orchestration: LangChain (chains for LLM prompting); Hugging Face Transformers (host Llama-3 fine-tuned on child narratives for persona adherence).
TTS Integration: ElevenLabs API (text-to-speech with emotion tags; stream MP3/WAV blobs).
3D Model Generation: TripoSR (open-source text-to-3D via Hugging Face; generates mesh from prompt in ~10s on GPU). Fallback: Stable Zero123 for image-to-3D if text-only. Post-process with Blender Python API (headless) for rigging/optimization.
Networking: WebSockets (via FastAPI-WebSocket) for real-time; HTTP/2 for asset downloads.
Queueing: Celery + Redis for async tasks (e.g., heavy 3D gen).
Deployment: Dockerized; Kubernetes for scaling; NGINX reverse proxy.
Monitoring: Prometheus + Grafana for latency/error tracking.
Environment: Python 3.11+; GPU support (CUDA 12+) for AI/3D gen.

Hardware Needs: At least 1x NVIDIA A10 GPU for inference/gen; scale to 4x for prod.
Key Features
1. API Endpoints

POST /session/init: Initialize user session with character choice (Gavel/Scales/Weights); returns session ID, assistant voice config, and initial dialogue prompt.
GET /dialogue/{session_id}: Fetch next child line (LLM-generated); params: user_action (e.g., "hesitate").
POST /tts/synthesize: Input: text + emotion (e.g., "hopeful"); Output: audio URL/stream; caches common phrases.
POST /3d/generate: Input: text prompt (e.g., "bombed-out child's bedroom with cracked music box"); Output: GLTF URL + metadata (bounding box, LOD variants); async via Celery.
WS /ws/dialogue/{session_id}: Real-time stream for live interactions (e.g., child probes: "Do you have a little boy?"); bidirectional for user voice input if extended.
GET /story/branch/{session_id}: Retrieve vignette data (e.g., House 3 memory script); includes pre-gen 3D hooks.
POST /imprint/capture: Log imprint event (timestamp, emotion peak); no data stored, just analytics.

2. Database Schema

sessions (id: UUID PK, user_id: str, character: enum[Gavel,Scales,Weights], start_ts: datetime, progress: json[house_num, branches]).
dialogue_cache (id: UUID PK, session_id: FK, prompt: text, response: json[text, emotion], ts: datetime, hits: int).
3d_assets (id: UUID PK, prompt: text, gltf_url: str, metadata: json[vertices, textures], gen_ts: datetime, usage_count: int).
vignettes (id: int PK, house_num: int, base_prompt: text, objects: json[metaphoric_items], memory_script: text).
Indexes: On session_id for fast lookups; TTL on cache (1hr).

3. AI Dialogue Generation

LangChain chain: Prompt template enforces child persona ("Respond as a 7yo war orphan: simple words, allusions to trauma, no adult questions. E.g., 'Do you... have a little girl? Like me hiding?'").
Fine-tuned model: Llama-3-8B (Hugging Face hub: "echoes-mercy-child-v1"); safety guardrails (reject off-topic via moderation API).
Branching: If user hands object, append context ("User gave music box → evoke lullaby memory").

4. TTS Processing

ElevenLabs client: Tag emotions (e.g., "trembling" for separation story); voice: Custom "Lost Child" (young, neutral accent).
Streaming: Chunk audio for WebSocket; fallback to pre-recorded for high-load.
Rate: 1-2s latency; cache 80% of lines (e.g., core pleas like "Are you my mother?").

5. AI-Driven 3D Model Generator

Core Flow: Client sends prompt (derived from vignette, e.g., "ethereal mother hugging child in golden light, war ruins background"); server queues to TripoSR (text → point cloud → mesh).
Enhancements: Post-gen: Blender script auto-rigs (e.g., add bone for hug animation); optimize (decimate polys <10k for VR); generate variants (damaged vs. intact).
Integration: On vignette entry, server pre-fetches or gens model; sends GLTF to client via signed S3 URL (store in MinIO for self-host).
Fallbacks: If gen fails (>30s), serve static asset; cache hits for repeated prompts.
Customization: Tie to user choice (e.g., Scales: add oceanic debris textures via prompt injection).
Limits: 1 gen/user/session; watermark models with metadata for traceability.

6. Session and Security Management

JWT auth for sessions; CORS for Godot origins.
Logging: Structured (ELK stack) for AI outputs (anonymized).
Scalability: Async endpoints; GPU queue for 3D (max 5 concurrent).

User Stories
User stories describe server behaviors from the perspective of the VR client or system admin, in the format: As a [role], I want [feature] so that [benefit]. Assume a session with Gavel selected, mid-vignette.
Initialization and Setup

As the VR client, I want to POST /session/init with {"character": "Gavel"} and receive {"session_id": "uuid", "assistant_voice": "Scales_raspy", "initial_prompt": "Child approaches: 'Are you my mother?'"}, so that I can bootstrap the narrative without local storage.
As a system admin, I want to seed the vignettes table with base data (e.g., House 1: {"prompt": "family hiding under table during bombing"}), so that procedural gens have consistent starting points.

Dialogue and Reactivity

As the VR client, I want to GET /dialogue/{session_id}?action=hand_object&object=music_box and receive {"text": "This... plays her song. Remember?", "emotion": "nostalgic"}, so that the child's response feels reactive and child-like without client-side AI.
As the VR client, I want WS /ws/dialogue to stream TTS audio chunks for the response, triggered by lip-sync ready signal, so that voice plays in real-time without buffering delays.

TTS Synthesis

As the VR client, I want to POST /tts/synthesize with {"text": "Mother, is that you? Really you?", "emotion": "hopeful_tremble"} and get a streaming MP3 URL, so that emotional delivery enhances immersion (e.g., voice cracks on "really").
As the server, I want to cache synthesized clips in Redis (key: hash(text+emotion)) with 1hr TTL, so that repeated lines (e.g., reunion hug) serve instantly.

3D Model Generation

As the VR client, I want to POST /3d/generate with {"prompt": "cracked locket on rubble floor, war-torn bedroom, metaphoric for lost family"} during vignette entry, and receive {"gltf_url": "s3://assets/model.glb", "bounds": [x,y,z]}, so that I can load a custom, AI-generated prop for handoff interaction.
As the VR client, I want the server to inject character context (e.g., "include judicial scales motif" for Gavel choice) into the prompt automatically, so that models tie into the time-traveler lore without extra client logic.
As a system admin, I want Celery tasks to log 3D gen metrics (duration, poly count) to PostgreSQL, so that I can monitor GPU usage and optimize prompts for faster renders (<10s avg).

Branching and Imprint

As the VR client, I want GET /story/branch/{session_id}?house=5 to return {"script": "Bad men at door—hide!", "3d_prompt": "shadowy figures in doorway", "radio_line": "Scales: 'This one's mine—choked on fear like seawater.'"}, so that progression adapts to session state.
As the VR client, I want POST /imprint/capture with {"timestamp": "reunion_hug", "peak_emotion": "relief"} to log anonymously, so that aggregate data helps refine future AI prompts (e.g., more "peaceful" imprints).

Monitoring and Maintenance

As a system admin, I want rate-limiting on /3d/generate (1/min per session) via FastAPI middleware, so that free-tier GPU doesn't overload during peaks.
As the server, I want fallback logic: If TripoSR times out, query 3d_assets for similar prompt (cosine similarity via embeddings) and serve cached GLTF, so that users never see a blank vignette.